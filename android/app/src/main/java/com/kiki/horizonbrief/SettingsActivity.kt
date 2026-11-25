package com.kiki.horizonbrief

import android.app.Activity
import android.content.Context
import android.graphics.PixelFormat
import android.os.Build
import android.os.Bundle
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.view.WindowManager
import android.view.animation.DecelerateInterpolator
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView

/**
 * 设置面板。
 *
 * 视觉与动效目标（用户 2026-11-25 提的）：
 *   - 不是原生下拉菜单，而是「从右上角那个胶囊原地放大成整块面板」，返回时缩回原处；
 *   - 面板是毛玻璃：Android 12+ 走真正的系统 blur-behind（窗口透明 + FLAG_BLUR_BEHIND），
 *     更低版本退化为「深色半透 + 冷色描边 + 顶部微亮渐变」，靠材质感而不是真模糊。
 *
 * 与主界面的关系：所有会动 WebView 的操作（重新加载 / 回顶部 / 字号 / 检查更新）
 * 都通过 [SettingsBridge] 直接回调 MainActivity，面板不会被原生对话框打断。
 */
class SettingsActivity : Activity() {

    private lateinit var panel: View
    private lateinit var scrim: View
    private var ax = -1f
    private var ay = -1f
    private var aw = 0
    private var ah = 0
    private var advanced = false
    private var closing = false

    private val zoomValues = intArrayOf(85, 100, 115, 130)
    private val zoomLabels = arrayOf("小", "标准", "大", "特大")

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        overridePendingTransition(0, 0)
        setContentView(R.layout.activity_settings)

        // 透明窗口 + 硬件加速：blur-behind 在这两个条件下才生效
        window.setFormat(PixelFormat.TRANSLUCENT)
        panel = findViewById(R.id.panel)
        scrim = findViewById(R.id.scrim)

        advanced = intent?.getBooleanExtra(EXTRA_ADVANCED, false) ?: false
        ax = intent?.getFloatExtra(EXTRA_AX, -1f) ?: -1f
        ay = intent?.getFloatExtra(EXTRA_AY, -1f) ?: -1f
        aw = intent?.getIntExtra(EXTRA_AW, 0) ?: 0
        ah = intent?.getIntExtra(EXTRA_AH, 0) ?: 0

        setupGlass()
        bindRows()
        buildZoomChips()
        findViewById<TextView>(R.id.closeBtn).setOnClickListener { closePanel() }
        scrim.setOnClickListener { closePanel() }

        panel.scaleX = 0.16f
        panel.scaleY = 0.16f
        panel.alpha = 0f
        scrim.alpha = 0f
    }

    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        if (hasFocus && !closing && panel.scaleX < 1f) playEnter()
    }

    /** 毛玻璃：31+ 用系统 blur-behind；更早版本靠半透深底 + 描边撑材质感。 */
    private fun setupGlass() {
        val canBlur = Build.VERSION.SDK_INT >= Build.VERSION_CODES.S
        scrim.setBackgroundColor(
            if (canBlur) 0x8C0B1119.toInt() else 0xE60B1119.toInt()
        )
        if (canBlur) {
            window.addFlags(WindowManager.LayoutParams.FLAG_BLUR_BEHIND)
            val attrs = window.attributes
            attrs.blurBehindRadius = dp(this, 26)
            window.attributes = attrs
        }
    }

    private fun playEnter() {
        panel.post {
            val loc = IntArray(2)
            panel.getLocationOnScreen(loc)
            if (ax >= 0f && ay >= 0f) {
                // 支点落在设置胶囊中心：放大时看起来就是它自己在撑开
                panel.pivotX = ax + aw / 2f - loc[0]
                panel.pivotY = ay + ah / 2f - loc[1]
            } else {
                panel.pivotX = panel.width.toFloat()
                panel.pivotY = dp(this, 40).toFloat()
            }
            panel.animate()
                .scaleX(1f).scaleY(1f).alpha(1f)
                .setDuration(340)
                .setInterpolator(DecelerateInterpolator(1.6f))
                .start()
            scrim.animate().alpha(1f).setDuration(300).start()
        }
    }

    private fun closePanel() = closePanel(null)

    private fun closePanel(then: (() -> Unit)?) {
        if (closing) return
        closing = true
        panel.animate()
            .scaleX(0.16f).scaleY(0.16f).alpha(0f)
            .setDuration(200)
            .setInterpolator(DecelerateInterpolator(1.4f))
            .withEndAction {
                then?.invoke()
                finish()
                overridePendingTransition(0, 0)
            }
            .start()
        scrim.animate().alpha(0f).setDuration(200).start()
    }

    override fun onBackPressed() {
        closePanel()
    }

    // ---------------------------------------------------------------- 行绑定

    private fun bindRows() {
        val version = runCatching {
            packageManager.getPackageInfo(packageName, 0).versionName
        }.getOrNull() ?: ""
        findViewById<TextView>(R.id.panelSub).text =
            "KIKINEWS · v$version" + if (advanced) "" else "　长按「设置」6 秒解锁高级"

        bindRow(R.id.rowReload, "重新加载", "重新请求当前这一期日报", R.drawable.ic_kv_refresh, CYAN, "") {
            closePanel { SettingsBridge.act(ACT_RELOAD) }
        }
        bindRow(R.id.rowHard, "强制刷新", "清掉网页缓存再加载，排版异常时用", R.drawable.ic_kv_clear, MINT, "") {
            closePanel { SettingsBridge.act(ACT_HARD_RELOAD) }
        }
        bindRow(R.id.rowTop, "回到顶部", "跳回报头顶部", R.drawable.ic_kv_top, BLUE, "") {
            closePanel { SettingsBridge.act(ACT_TOP) }
        }
        bindRow(R.id.rowZoom, "正文字号", "只影响网页正文，不影响报头装饰", R.drawable.ic_kv_text, CYAN, "") {}
        bindRow(
            R.id.rowUpdate, "检查更新",
            "从 GitHub Pages 拉版本清单",
            R.drawable.ic_kv_update, AMBER, ""
        ) {
            closePanel { SettingsBridge.act(ACT_UPDATE) }
        }

        val advViews = listOf(R.id.advTitle, R.id.rowBrowser, R.id.rowCopy)
        advViews.forEach { findViewById<View>(it).visibility = if (advanced) View.VISIBLE else View.GONE }
        if (advanced) {
            bindRow(R.id.rowBrowser, "在浏览器中打开", "用系统浏览器看同一期", R.drawable.ic_kv_browser, BLUE, "") {
                closePanel { SettingsBridge.act(ACT_BROWSER) }
            }
            bindRow(R.id.rowCopy, "复制日报链接", "拷到剪贴板，方便发给别人", R.drawable.ic_kv_copy, MUTED, "") {
                closePanel { SettingsBridge.act(ACT_COPY) }
            }
        }
    }

    private fun bindRow(
        id: Int,
        title: String,
        sub: String,
        icon: Int,
        tint: Int,
        right: String,
        onClick: () -> Unit
    ) {
        val root = findViewById<View>(id)
        root.findViewById<TextView>(R.id.row_title).text = title
        val subView = root.findViewById<TextView>(R.id.row_sub)
        if (sub.isNullOrBlank()) subView.visibility = View.GONE else {
            subView.text = sub
            subView.visibility = View.VISIBLE
        }
        root.findViewById<ImageView>(R.id.row_icon).apply {
            if (icon >= 0) {
                setImageResource(icon)
                setColorFilter(tint)
            }
        }
        val rightView = root.findViewById<TextView>(R.id.row_right)
        if (right.isNullOrBlank()) rightView.visibility = View.GONE else {
            rightView.text = right
            rightView.visibility = View.VISIBLE
        }
        root.setOnClickListener { onClick() }
    }

    /** 字号四档做成并排 chip，点一下即时生效，不用再弹一个原生单选对话框。 */
    private fun buildZoomChips() {
        val box = findViewById<LinearLayout>(R.id.zoomChips)
        box.removeAllViews()
        val current = SettingsBridge.zoom()
        zoomValues.forEachIndexed { i, v ->
            val chip = TextView(this)
            chip.text = "${zoomLabels[i]} $v%"
            chip.textSize = 12f
            chip.gravity = Gravity.CENTER
            chip.setPadding(dp(this, 4), dp(this, 10), dp(this, 4), dp(this, 10))
            chip.background = getDrawable(
                if (v == current) R.drawable.bg_chip_on else R.drawable.bg_chip_off
            )
            chip.setTextColor(if (v == current) MINT else 0xFFB4C0D4.toInt())
            val lp = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
            lp.leftMargin = dp(this, 3)
            lp.rightMargin = dp(this, 3)
            chip.layoutParams = lp
            chip.setOnClickListener {
                SettingsBridge.act(ACT_ZOOM, v)
                buildZoomChips()
            }
            box.addView(chip)
        }
    }

    companion object {
        const val EXTRA_ADVANCED = "advanced"
        const val EXTRA_AX = "ax"
        const val EXTRA_AY = "ay"
        const val EXTRA_AW = "aw"
        const val EXTRA_AH = "ah"

        const val ACT_RELOAD = "reload"
        const val ACT_HARD_RELOAD = "hardReload"
        const val ACT_TOP = "top"
        const val ACT_ZOOM = "zoom"
        const val ACT_UPDATE = "update"
        const val ACT_BROWSER = "browser"
        const val ACT_COPY = "copy"

        private val CYAN = 0xFF4FD1C5.toInt()
        private val MINT = 0xFF7FD1A8.toInt()
        private val BLUE = 0xFF7EA8F0.toInt()
        private val AMBER = 0xFFF0C879.toInt()
        private val MUTED = 0xFFB0BACB.toInt()

        private fun dp(ctx: Context, v: Int): Int =
            (ctx.resources.displayMetrics.density * v).toInt()
    }
}

/**
 * 设置面板与 MainActivity 之间的单向桥。
 *
 * 面板是个独立 Activity，但所有操作对象（WebView / prefs）都在 MainActivity 里；
 * 用 startActivityForResult 的话每点一次就得关面板，体验会断。
 * 这里挂一个弱引用式的直连：MainActivity 在 onCreate 时登记、onDestroy 时撤销。
 */
object SettingsBridge {
    @Volatile
    var host: MainActivity? = null

    fun act(action: String, arg: Int = 0) {
        host?.onSettingsAction(action, arg)
    }

    fun zoom(): Int = host?.currentZoom() ?: 100
}
