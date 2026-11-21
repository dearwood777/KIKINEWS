package com.kiki.horizonbrief

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.net.Uri
import android.os.Build
import android.provider.Settings
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.core.content.FileProvider
import org.json.JSONObject
import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest
import java.util.concurrent.Executors

/**
 * 应用自更新：只在 GitHub Pages 上放一个 version.json 和对应的 apk，
 * App 启动时（或手动「检查更新」时）拉一次，比 versionCode 决定要不要提示。
 *
 * 为什么不用 Google Play 的 in-app update：这个 App 不走 Play 分发，
 * Play Core 的更新 API 在侧载安装的包里永远返回不可用。
 * 这套做法和 GitHub 上几个自更新库（SelfUpdatingApp / APK-MultiUpdate）同源：
 * 版本清单 → 下载 → FileProvider 交给系统安装器。
 */
object UpdateChecker {

    private const val MANIFEST_URL = "https://dearwood777.github.io/KIKINEWS/app/version.json"
    private const val PREF = "horizon"
    private const val KEY_PROMPTED = "update_prompted_code"

    private val executor = Executors.newSingleThreadExecutor()

    private data class Remote(
        val code: Long,
        val name: String,
        val apkUrl: String,
        val sha256: String,
        val notes: String,
    )

    fun check(activity: Activity, manual: Boolean = false) {
        if (activity.isFinishing) return
        executor.execute {
            val remote = runCatching { fetch() }.getOrNull()
            activity.runOnUiThread {
                if (activity.isFinishing) return@runOnUiThread
                if (remote == null) {
                    if (manual) toast(activity, "检查更新失败，请稍后再试")
                    return@runOnUiThread
                }
                val local = localVersionCode(activity)
                when {
                    remote.code <= local -> if (manual) toast(activity, "已是最新版本 ${remote.name}")
                    else -> {
                        val prefs = activity.getSharedPreferences(PREF, Context.MODE_PRIVATE)
                        val prompted = prefs.getLong(KEY_PROMPTED, 0L)
                        // 同一个版本只自动提醒一次，避免每次打开都弹
                        if (!manual && prompted == remote.code) return@runOnUiThread
                        showDialog(activity, remote, prefs)
                    }
                }
            }
        }
    }

    private fun showDialog(activity: Activity, remote: Remote, prefs: SharedPreferences) {
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
                download(activity, remote)
            }
            .setNegativeButton("稍后") { _, _ ->
                prefs.edit().putLong(KEY_PROMPTED, remote.code).apply()
            }
            .setCancelable(true)
            .show()
    }

    private fun download(activity: Activity, remote: Remote) {
        toast(activity, "开始下载 ${remote.name} …")
        executor.execute {
            val file = runCatching { fetchApk(activity, remote) }.getOrNull()
            activity.runOnUiThread {
                if (file == null) {
                    toast(activity, "下载失败，请检查网络后重试")
                } else {
                    install(activity, file)
                }
            }
        }
    }

    private fun fetchApk(activity: Activity, remote: Remote): File? {
        val dir = File(activity.cacheDir, "apk").apply { mkdirs() }
        val target = File(dir, "kikinews-${remote.name}.apk")
        if (target.exists() && target.length() > 0) {
            if (remote.sha256.isBlank() || sha256(target) == remote.sha256) return target
            target.delete()
        }
        val conn = (URL(remote.apkUrl).openConnection() as HttpURLConnection).apply {
            connectTimeout = 15000
            readTimeout = 30000
            instanceFollowRedirects = true
        }
        conn.inputStream.use { input ->
            target.outputStream().use { out -> input.copyTo(out) }
        }
        conn.disconnect()
        if (remote.sha256.isNotBlank() && sha256(target) != remote.sha256) {
            target.delete()
            return null
        }
        return target
    }

    private fun install(activity: Activity, file: File) {
        // Android 8+ 需要用户先授予「安装未知应用」，否则系统直接丢弃意图
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O &&
            !activity.packageManager.canRequestPackageInstalls()
        ) {
            toast(activity, "请允许本应用安装未知来源应用后重试")
            runCatching {
                activity.startActivity(
                    Intent(
                        Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,
                        Uri.parse("package:${activity.packageName}")
                    )
                )
            }
            return
        }
        val uri = FileProvider.getUriForFile(
            activity, "${activity.packageName}.files", file
        )
        val intent = Intent(Intent.ACTION_VIEW).apply {
            setDataAndType(uri, "application/vnd.android.package-archive")
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_ACTIVITY_NEW_TASK)
        }
        runCatching { activity.startActivity(intent) }
            .onFailure { toast(activity, "无法调起安装器：${it.message}") }
    }

    private fun fetch(): Remote? {
        val conn = (URL("$MANIFEST_URL?t=${System.currentTimeMillis()}")
            .openConnection() as HttpURLConnection).apply {
            connectTimeout = 12000
            readTimeout = 12000
            setRequestProperty("Cache-Control", "no-cache")
        }
        val body = conn.inputStream.bufferedReader().use { it.readText() }
        conn.disconnect()
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

    private fun toast(activity: Activity, msg: String) {
        activity.runOnUiThread {
            Toast.makeText(activity, msg, Toast.LENGTH_SHORT).show()
        }
    }
}
