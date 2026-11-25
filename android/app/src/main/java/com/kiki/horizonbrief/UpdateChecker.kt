package com.kiki.horizonbrief

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.net.Uri
import android.os.Build
import android.provider.Settings
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.core.content.FileProvider
import org.json.JSONObject
import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicBoolean

/**
 * 应用自更新：只在 GitHub Pages 上放一个 version.json 和对应的 apk，
 * App 启动时（或手动「检查更新」时）拉一次，比 versionCode 决定要不要提示。
 *
 * 为什么不用 Google Play 的 in-app update：这个 App 不走 Play 分发，
 * Play Core 的更新 API 在侧载安装的包里永远返回不可用。
 *
 * —— 2026-11-25 修的两个坑 ——
 * 1) 检查与下载原来共用 `newSingleThreadExecutor()` 一条线程。下载一旦卡在
 *    socket 上（弱网/墙/Pages 慢），后面每一次「检查更新」的任务都排在队列里
 *    永远轮不到执行；配合"提交任务后才发 toast"，用户看到的就是
 *    「闪一下正在检查更新，然后就没了」。现在两条独立线程 + 防重入标志。
 * 2) 下载全程零反馈，失败只有一句 1 秒的 toast，用户分不清"在传"还是"死了"。
 *    现在有确定进度框（百分比 + 已传/总量），失败弹模态对话框写清原因，
 *    并给「重试」「用浏览器下载」两个出口。
 *
 * 另外把「允许安装未知应用」的检查提到下载之前：没有这个权限，包下完也白下，
 * 以前是下完才 toast 一句、接着跳设置页，很多人根本没看见。
 */
object UpdateChecker {

    private const val MANIFEST_URL = "https://dearwood777.github.io/KIKINEWS/app/version.json"
    private const val PREF = "horizon"
    private const val KEY_PROMPTED = "update_prompted_code"

    /** 检查更新与下载各用一条线程，互不排队阻塞。 */
    private val checkPool = Executors.newSingleThreadExecutor()
    private val downloadPool = Executors.newSingleThreadExecutor()

    private val checking = AtomicBoolean(false)
    private val downloading = AtomicBoolean(false)

    /** 下载完但因缺少安装权限没装成，等用户从系统设置回来后接着装。 */
    @Volatile
    private var pendingApk: File? = null

    /** 最近一次要下载的版本，供"重试"和"用浏览器下载"复用。 */
    @Volatile
    private var lastRemote: Remote? = null

    private data class Remote(
        val code: Long,
        val name: String,
        val apkUrl: String,
        val sha256: String,
        val notes: String,
    )

    fun check(activity: Activity, manual: Boolean = false) {
        if (activity.isFinishing) return
        // 防重入：连点只提示，不往队列里堆任务
        if (!checking.compareAndSet(false, true)) {
            if (manual) toast(activity, "正在检查更新，请稍候…")
            return
        }
        // 手动检查先给一个即时反馈，否则用户会觉得"点了没反应"
        if (manual) toast(activity, "正在检查更新…")
        checkPool.execute {
            try {
                val result = runCatching { fetch() }
                val remote = result.getOrNull()
                val error = result.exceptionOrNull()
                activity.runOnUiThread {
                    if (activity.isFinishing) return@runOnUiThread
                    if (remote == null) {
                        if (manual) {
                            val reason = when {
                                error != null -> error.message ?: error.javaClass.simpleName
                                else -> "更新清单内容不完整"
                            }
                            info(
                                activity,
                                "检查更新失败",
                                "没能连上更新服务器。\n\n原因：$reason\n\n请确认网络可用后重试；" +
                                    "如果反复失败，可以直接下载最新安装包覆盖安装。"
                            )
                        }
                        return@runOnUiThread
                    }
                    val local = localVersionCode(activity)
                    if (remote.code <= local) {
                        if (manual) {
                            info(
                                activity,
                                "已是最新版本",
                                "当前版本：v${localVersionName(activity)}（$local）\n" +
                                    "线上版本：v${remote.name}（${remote.code}）\n\n已经是最新版本，无需更新。"
                            )
                        }
                        return@runOnUiThread
                    }
                    val prefs = activity.getSharedPreferences(PREF, Context.MODE_PRIVATE)
                    // 同一个版本只自动提醒一次，避免每次打开都弹
                    if (!manual && prefs.getLong(KEY_PROMPTED, 0L) == remote.code) return@runOnUiThread
                    showDialog(activity, remote, prefs)
                }
            } finally {
                checking.set(false)
            }
        }
    }

    /**
     * 从系统「安装未知应用」设置页回来时调用（MainActivity.onResume）。
     * 手里攒着已下载好的包、权限也拿到了，就直接调起安装器。
     */
    fun resumePendingInstall(activity: Activity) {
        val file = pendingApk ?: return
        if (!canInstall(activity)) return
        pendingApk = null
        activity.runOnUiThread { install(activity, file) }
    }

    /** 明确的模态提示：点一下一定看得到，不会像 toast 那样一闪而过 */
    private fun info(activity: Activity, title: String, message: String) {
        if (activity.isFinishing) return
        AlertDialog.Builder(activity)
            .setTitle(title)
            .setMessage(message)
            .setPositiveButton("知道了", null)
            .setCancelable(true)
            .show()
    }

    private fun showDialog(activity: Activity, remote: Remote, prefs: SharedPreferences) {
        lastRemote = remote
        val message = buildString {
            append("当前版本：").append(localVersionName(activity)).append('\n')
            append("新版本：").append(remote.name)
            if (remote.notes.isNotBlank()) append("\n\n").append(remote.notes)
        }
        AlertDialog.Builder(activity)
            .setTitle("发现新版本")
            .setMessage(message)
            .setPositiveButton("下载并安装") { _, _ ->
                prefs.edit().putLong(KEY_PROMPTED, remote.code).apply()
                startDownload(activity, remote)
            }
            .setNegativeButton("稍后") { _, _ ->
                prefs.edit().putLong(KEY_PROMPTED, remote.code).apply()
            }
            .setCancelable(true)
            .show()
    }

    /** 下载前的分岔：没安装权限就先去要，别等 2.5MB 下完才发现装不上。 */
    private fun startDownload(activity: Activity, remote: Remote) {
        lastRemote = remote
        if (!canInstall(activity)) {
            askInstallPermission(activity, remote)
            return
        }
        if (!downloading.compareAndSet(false, true)) {
            toast(activity, "正在下载中，请稍候…")
            return
        }

        val cancelled = AtomicBoolean(false)
        var dialog: AlertDialog? = null

        // 进度框：百分比 + 已传 MB / 总 MB，不可点外部取消
        val bar = ProgressBar(activity, null, android.R.attr.progressBarStyleHorizontal).apply {
            max = 100
            progress = 0
        }
        val label = TextView(activity).apply {
            text = "准备连接…"
            textSize = 13f
        }
        val box = LinearLayout(activity).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(activity, 22), dp(activity, 18), dp(activity, 22), dp(activity, 4))
            addView(
                bar,
                LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT
                )
            )
            addView(label)
        }

        activity.runOnUiThread {
            dialog = AlertDialog.Builder(activity)
                .setTitle("正在下载 ${remote.name}")
                .setView(box)
                .setNegativeButton("取消", null)
                .setCancelable(false)
                .create()
            dialog?.show()
            dialog?.getButton(AlertDialog.BUTTON_NEGATIVE)?.setOnClickListener {
                cancelled.set(true)
                dialog?.dismiss()
            }
        }

        downloadPool.execute {
            val outcome = runCatching {
                fetchApk(activity, remote, cancelled) { pct, done, total ->
                    activity.runOnUiThread {
                        if (dialog?.isShowing != true) return@runOnUiThread
                        if (pct >= 0) bar.progress = pct
                        label.text = if (total > 0) {
                            "${if (pct >= 0) pct else 0}% · ${mb(done)} / ${mb(total)} MB"
                        } else {
                            "已下载 ${mb(done)} MB"
                        }
                    }
                }
            }.getOrElse { Outcome.Fail(it.message ?: it.javaClass.simpleName) }

            activity.runOnUiThread {
                dialog?.dismiss()
                downloading.set(false)
                if (activity.isFinishing) return@runOnUiThread
                when (outcome) {
                    is Outcome.Ok -> install(activity, outcome.file)
                    Outcome.Canceled -> toast(activity, "已取消下载")
                    is Outcome.Fail -> {
                        // 失败就把"已提示过"的记录清掉，下次自动检查还能再提醒
                        activity.getSharedPreferences(PREF, Context.MODE_PRIVATE)
                            .edit().remove(KEY_PROMPTED).apply()
                        showFailDialog(activity, remote, outcome.reason)
                    }
                }
            }
        }
    }

    private fun showFailDialog(activity: Activity, remote: Remote, reason: String) {
        AlertDialog.Builder(activity)
            .setTitle("下载失败")
            .setMessage(
                "原因：$reason\n\n" +
                    "可以直接用浏览器下载同一个安装包（${remote.name}），下载完点开安装即可。"
            )
            .setPositiveButton("重试") { _, _ -> startDownload(activity, remote) }
            .setNegativeButton("用浏览器下载") { _, _ -> openInBrowser(activity, remote.apkUrl) }
            .setNeutralButton("知道了", null)
            .setCancelable(true)
            .show()
    }

    private fun askInstallPermission(activity: Activity, remote: Remote) {
        lastRemote = remote
        AlertDialog.Builder(activity)
            .setTitle("需要允许安装应用")
            .setMessage(
                "系统默认不允许 App 自己安装应用。\n\n" +
                    "点「去设置」后，在接下来的页面里打开「允许来自此来源的应用」，" +
                    "返回本应用后会自动接着安装。"
            )
            .setPositiveButton("去设置") { _, _ -> openInstallSettings(activity) }
            .setNegativeButton("取消", null)
            .setCancelable(true)
            .show()
    }

    private sealed class Outcome {
        data class Ok(val file: File) : Outcome()
        data class Fail(val reason: String) : Outcome()
        object Canceled : Outcome()
    }

    private fun fetchApk(
        activity: Activity,
        remote: Remote,
        cancelled: AtomicBoolean,
        progress: (pct: Int, done: Long, total: Long) -> Unit,
    ): Outcome {
        val dir = File(activity.cacheDir, "apk").apply { mkdirs() }
        val target = File(dir, "kikinews-${remote.name}.apk")

        // 已经有一份校验通过的包，直接复用：点重试时不用重新下 2.5MB
        if (remote.sha256.isNotBlank() && target.exists() && target.length() > 0 &&
            sha256(target) == remote.sha256
        ) {
            progress(100, target.length(), target.length())
            return Outcome.Ok(target)
        }
        if (target.exists()) target.delete()

        var conn: HttpURLConnection? = null
        try {
            conn = (URL(remote.apkUrl).openConnection() as HttpURLConnection).apply {
                connectTimeout = 20000
                readTimeout = 45000
                instanceFollowRedirects = true
                setRequestProperty("User-Agent", "KIKINEWS-Updater/1.0")
                setRequestProperty("Cache-Control", "no-cache")
            }
            val code = conn.responseCode
            if (code != HttpURLConnection.HTTP_OK) {
                return Outcome.Fail("服务器返回 HTTP $code，安装包可能还没发布完成")
            }
            val total = conn.contentLengthLong
            conn.inputStream.use { input ->
                target.outputStream().use { out ->
                    val buf = ByteArray(8192)
                    var done = 0L
                    var lastPct = -2
                    while (true) {
                        if (cancelled.get()) {
                            target.delete()
                            return Outcome.Canceled
                        }
                        val n = input.read(buf)
                        if (n <= 0) break
                        out.write(buf, 0, n)
                        done += n
                        val pct = if (total > 0) ((done * 100) / total).toInt() else -1
                        if (pct != lastPct) {
                            lastPct = pct
                            progress(pct, done, total)
                        }
                    }
                }
            }
        } catch (t: Throwable) {
            target.delete()
            if (cancelled.get()) return Outcome.Canceled
            return Outcome.Fail(t.message ?: t.javaClass.simpleName)
        } finally {
            runCatching { conn?.disconnect() }
        }

        if (remote.sha256.isNotBlank() && sha256(target) != remote.sha256) {
            target.delete()
            return Outcome.Fail("安装包校验不通过（传输中被改动或没下完整），请重试")
        }
        return Outcome.Ok(target)
    }

    private fun canInstall(activity: Activity): Boolean =
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            runCatching { activity.packageManager.canRequestPackageInstalls() }.getOrDefault(false)
        } else {
            true
        }

    private fun openInstallSettings(activity: Activity) {
        runCatching {
            activity.startActivity(
                Intent(
                    Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,
                    Uri.parse("package:${activity.packageName}")
                )
            )
        }.onFailure { toast(activity, "打不开系统设置页，请手动到应用权限里开启") }
    }

    private fun install(activity: Activity, file: File) {
        // 权限在这次会话里可能刚被撤销，装之前再确认一次
        if (!canInstall(activity)) {
            pendingApk = file
            val remote = lastRemote
            if (remote != null) {
                askInstallPermission(activity, remote)
            } else {
                toast(activity, "请允许安装未知应用后重试")
            }
            return
        }
        val uri = runCatching {
            FileProvider.getUriForFile(activity, "${activity.packageName}.files", file)
        }.getOrNull()
        if (uri == null) {
            toast(activity, "安装包路径异常，请用浏览器下载")
            return
        }
        val intent = Intent(Intent.ACTION_VIEW).apply {
            setDataAndType(uri, "application/vnd.android.package-archive")
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_ACTIVITY_NEW_TASK)
        }
        runCatching { activity.startActivity(intent) }
            .onFailure { toast(activity, "无法调起安装器：${it.message}") }
    }

    private fun openInBrowser(activity: Activity, url: String) {
        runCatching { activity.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url))) }
            .onFailure { toast(activity, "没有可用的浏览器") }
    }

    private fun fetch(): Remote? {
        var conn: HttpURLConnection? = null
        try {
            conn = (URL("$MANIFEST_URL?t=${System.currentTimeMillis()}")
                .openConnection() as HttpURLConnection).apply {
                connectTimeout = 12000
                readTimeout = 12000
                setRequestProperty("Cache-Control", "no-cache")
                setRequestProperty("User-Agent", "KIKINEWS-Updater/1.0")
            }
            if (conn.responseCode != HttpURLConnection.HTTP_OK) return null
            val body = conn.inputStream.bufferedReader().use { it.readText() }
            val json = JSONObject(body)
            val code = json.optLong("versionCode", 0L)
            val apk = json.optString("apk", "")
            if (code <= 0L || apk.isBlank()) return null
            return Remote(
                code = code,
                name = json.optString("versionName", code.toString()),
                apkUrl = apk,
                sha256 = json.optString("sha256", ""),
                notes = json.optString("notes", ""),
            )
        } finally {
            runCatching { conn?.disconnect() }
        }
    }

    private fun localVersionCode(activity: Activity): Long {
        val info = activity.packageManager.getPackageInfo(activity.packageName, 0)
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            info.longVersionCode
        } else {
            @Suppress("DEPRECATION")
            info.versionCode.toLong()
        }
    }

    private fun localVersionName(activity: Activity): String =
        runCatching {
            activity.packageManager.getPackageInfo(activity.packageName, 0).versionName
        }.getOrNull() ?: "未知"

    private fun sha256(file: File): String {
        val md = MessageDigest.getInstance("SHA-256")
        file.inputStream().use { input ->
            val buf = ByteArray(8192)
            while (true) {
                val n = input.read(buf)
                if (n <= 0) break
                md.update(buf, 0, n)
            }
        }
        return md.digest().joinToString("") { "%02x".format(it) }
    }

    private fun mb(bytes: Long): String = String.format("%.2f", bytes / 1024.0 / 1024.0)

    private fun dp(ctx: Context, v: Int): Int =
        (ctx.resources.displayMetrics.density * v).toInt()

    private fun toast(activity: Activity, msg: String) {
        activity.runOnUiThread {
            Toast.makeText(activity, msg, Toast.LENGTH_SHORT).show()
        }
    }
}
