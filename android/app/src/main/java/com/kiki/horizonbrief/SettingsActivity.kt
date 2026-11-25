package com.kiki.horizonbrief

import android.app.Activity
import android.content.Context
import android.graphics.Bitmap
import android.graphics.PixelFormat
import android.os.Build
import android.os.Bundle
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.view.WindowManager
import android.view.animation.DecelerateInterpolator
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import kotlin.math.min

/**
 * 设置小浮层。
 *
 * 形态定位（用户 2026-11-25 纠正过两次）：
 *   **不是全屏页面**，而是像 iOS 上下文菜单那样的一小块浮层 ——
 *   300dp 宽、右上角贴着「设置」胶囊往下挂、宽度收窄、每行右侧放当前值把空白填满。
 *
 * 毛玻璃：真模糊交给 [SettingsBackdrop]（PixelCopy 截背后网页 → 降采样 → 盒式模糊），
 * 铺在面板最底层；面板再叠一层很薄的冷色层压住饱和度。
 * 所以低版本机型（没有系统 blur-behind）看到的也是"背后被虚化"的玻璃，
 * 不是一块死黑。截图失败时退回半透明深色 + 细描边。
 */
class SettingsActivity : Activity() {

    private lateinit var root: View
    private lateinit var panel: View
    private lateinit var scrim: View
    private lateinit var blurBg: ImageView
    private lateinit var tintLayer: View
    private lateinit var chipsBox: LinearLayout

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
        window.setFormat(PixelFormat.TRANSLUCENT)

        root = findViewById(R.id.root)
        panel = findViewById(R.id.panel)
        scrim = findViewById(R.id.scrim)
        blurBg = findViewById(R.id.blurBg)
        tintLayer = findViewById(R.id.tintLayer)
        chipsBox = findViewById(R.id.zoomChips)

        advanced = intent?.getBooleanExtra(EXTRA_ADVANCED, false) ?: false
        ax = intent?.getFloatExtra(EXTRA_AX, -1f) ?: -1f
        ay = intent?.getFloatExtra(EXTRA_AY, -1f) ?: -1f
        aw = intent?.getIntExtra(EXTRA_AW, 0) ?: 0
        ah = intent?.getIntExtra(EXTRA_AH, 0) ?: 0

        setupGlass()
        placePanel()
        bindRows()
        buildZoomChips()

        findViewById<TextView>(R.id.closeBtn).setOnClickListener { closePanel() }
        scrim.setOnClickListener { closePanel() }

        panel.scaleX = 0.94f
        panel.scaleY = 0.94f
        panel.alpha = 0f
        panel.translationY = -dp(this, 10).toFloat()
        scrim.alpha = 0f
    }

    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        if (hasFocus && !closing && panel.alpha == 0f) playEnter()
    }

    /** 真模糊优先；截不到就退成半透明深玻璃。 */
    private fun setupGlass() {
        val blurred: Bitmap? = SettingsBackdrop.blurred
        if (blurred != null) {
            blurBg.setImageBitmap(blurred)
            blurBg.visibility = View.VISIBLE
            tintLayer.setBackgroundColor(0x8C121822.toInt())
            scrim.setBackgroundColor(0x4D000000)
        } else {
            blurBg.visibility = View.GONE
            tintLayer.setBackgroundColor(0xCC181B22.toInt())
            scrim.setBackgroundColor(0x73000000)
        }

        // 12+ 再叠一层系统 blur-behind：窗外的桌面/网页一起虚化，边缘更自然
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            window.addFlags(WindowManager.LayoutParams.FLAG_BLUR_BEHIND)
            val attrs = window.attributes
            attrs.blurBehindRadius = dp(this, 28)
            window.attributes = attrs
        }
    }

    /** 面板挂在胶囊正下方、右边缘与胶囊右边缘对齐；窄屏自动收窄。 */
    private fun placePanel() {
        panel.post {
            val rootLoc = IntArray(2)
            root.getLocationOnScreen(rootLoc)
            val lp = panel.layoutParams as FrameLayout.LayoutParams
            val screenW = resources.displayMetrics.widthPixels
            lp.width = min(dp(this, 300), screenW - dp(this, 24))
            lp.topMargin = if (ay >= 0f) {
                (ay + ah).toInt() - rootLoc[1] + dp(this, 8)
            } else {
                dp(this, 52)
            }
            lp.rightMargin = if (ax >= 0f) {
                (root.width - ((ax + aw).toInt() - rootLoc[0])).coerceAtLeast(dp(this, 8))
            } else {
                dp(this, 12)
            }
            panel.layoutParams = lp
        }
    }

    private fun playEnter() {
        panel.animate()
            .scaleX(1f).scaleY(1f).alpha(1f).translationY(0f)
            .setDuration(200)
            .setInterpolator(DecelerateInterpolator(1.6f))
            .start()
        scrim.animate().alpha(1f).setDuration(200).start()
    }

    private fun closePanel() = closePanel(null)

    private fun closePanel(then: (() -> Unit)?) {
        if (closing) return
        closing = true
        panel.animate()
            .scaleX(0.96f).scaleY(0.96f).alpha(0f)
            .translationY(-dp(this, 8).toFloat())
            .setDuration(150)
            .setInterpolator(DecelerateInterpolator(1.4f))
            .withEndAction {
                then?.invoke()
                finish()
                overridePendingTransition(0, 0)
            }
            .start()
        scrim.animate().alpha(0f).setDuration(150).start()
    }

    override fun onBackPressed() {
        closePanel()
    }

    // ---------------------------------------------------------------- 行绑定

    private fun bindRows() {
        val version = runCatching {
            packageManager.getPackageInfo(packageName, 0).versionName
        }.getOrNull() ?: ""
        findViewById<TextView>(R.id.panelTitle).text = "设置"

        bindRow(R.id.rowReload, "重新加载", R.drawable.ic_kv_refresh, CYAN, "") {
            closePanel { SettingsBridge.act(ACT_RELOAD) }
        }
        bindRow(R.id.rowHard, "强制刷新", R.drawable.ic_kv_clear, MINT, "清缓存") {
            closePanel { SettingsBridge.act(ACT_HARD_RELOAD) }
        }
        bindRow(R.id.rowTop, "回到顶部", R.drawable.ic_kv_top, BLUE, "") {
            closePanel { SettingsBridge.act(ACT_TOP) }
        }
        // 右侧直接显示当前档位，"右边空一块"的问题就是在这里补的
        bindRow(R.id.rowZoom, "正文字号", R.drawable.ic_kv_text, CYAN, "${SettingsBridge.zoom()}%") {
            toggleZoomChips()
        }
        bindRow(R.id.rowUpdate, "检查更新", R.drawable.ic_kv_update, AMBER, "v$version") {
            closePanel { SettingsBridge.act(ACT_UPDATE) }
        }

        val advViews = listOf(R.id.advGap, R.id.rowBrowser, R.id.rowCopy)
        advViews.forEach { findViewById<View>(it).visibility = if (advanced) View.VISIBLE else View.GONE }
        if (advanced) {
            bindRow(R.id.rowBrowser, "在浏览器中打开", R.drawable.ic_kv_browser, BLUE, "") {
                closePanel { SettingsBridge.act(ACT_BROWSER) }
            }
            bindRow(R.id.rowCopy, "复制日报链接", R.drawable.ic_kv_copy, MUTED, "") {
                closePanel { SettingsBridge.act(ACT_COPY) }
            }
            // 最后一行不画分隔线，免得贴到圆角上
            findViewById<View>(R.id.rowCopy).findViewById<View>(R.id.row_divider).visibility = View.GONE
        }
    }

    private fun bindRow(
        id: Int,
        title: String,
        icon: Int,
        tint: Int,
        right: String,
        onClick: () -> Unit
    ) {
        val root = findViewById<View>(id)
        root.findViewById<TextView>(R.id.row_title).text = title
        root.findViewById<ImageView>(R.id.row_icon).apply {
            setImageResource(icon)
            setColorFilter(tint)
        }
        val rightView = root.findViewById<TextView>(R.id.row_right)
        if (right.isBlank()) rightView.visibility = View.GONE else {
            rightView.text = right
            rightView.visibility = View.VISIBLE
        }
        root.setOnClickListener { onClick() }
    }

    private fun toggleZoomChips() {
        if (chipsBox.visibility == View.VISIBLE) {
            chipsBox.visibility = View.GONE
        } else {
            buildZoomChips()
            chipsBox.visibility = View.VISIBLE
        }
    }

    /** 字号四档做成并排 chip，点一下立刻生效，面板不关。 */
    private fun buildZoomChips() {
        chipsBox.removeAllViews()
        val current = SettingsBridge.zoom()
        zoomValues.forEachIndexed { i, v ->
            val chip = TextView(this)
            chip.text = "${zoomLabels[i]} $v%"
            chip.textSize = 11.5f
            chip.gravity = Gravity.CENTER
            chip.setPadding(dp(this, 2), dp(this, 8), dp(this, 2), dp(this, 8))
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
                // 标题右侧的当前值同步更新
                findViewById<View>(R.id.rowZoom).findViewById<TextView>(R.id.row_right).text = "$v%"
            }
            chipsBox.addView(chip)
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

        private val CYAN = 0xFF66D9CC.toInt()
        private val MINT = 0xFF8AD9B2.toInt()
        private val BLUE = 0xFF8FB4F2.toInt()
        private val AMBER = 0xFFE8C580.toInt()
        private val MUTED = 0xFFB0B8C6.toInt()

        private fun dp(ctx: Context, v: Int): Int =
            (ctx.resources.displayMetrics.density * v).toInt()
    }
}

/**
 * 设置面板与 MainActivity 之间的单向桥。
 * 面板是独立 Activity，要动的 WebView / prefs 都在 MainActivity 里，直接回调最省事。
 */
object SettingsBridge {
    @Volatile
    var host: MainActivity? = null

    fun act(action: String, arg: Int = 0) {
        host?.onSettingsAction(action, arg)
    }

    fun zoom(): Int = host?.currentZoom() ?: 100
}
