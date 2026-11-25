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
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import kotlin.math.min

/**
 * 设置小浮层。
 *
 * 形态定位（用户 2026-11-25 连续否决三版后定稿）：
 *   **不是全屏页面**，是 iOS 上下文菜单那样的一小块浮层。
 *
 * v1.6.013/014 踩的坑：Activity 窗口是 match_parent 全屏（windowIsFloating=false），
 * 里面再放一块 300dp 面板 —— 360dp 窄屏上 300dp 就是 83% 屏宽，观感等于全屏。
 * 现在改成 **窗口本身就是小浮窗**（Dialog 主题 + windowIsFloating=true），
 * 宽度由 [placeWindow] 的 window.setLayout() 决定，物理上不可能铺满屏幕。
 *
 * 毛玻璃：真模糊交给 [SettingsBackdrop]（PixelCopy 截背后网页 → 降采样 → 盒式模糊），
 * 铺在浮层最底层；再叠一层很薄的冷色层压住饱和度。低版本没有系统 blur-behind
 * 也是"背后被虚化"的玻璃，不是死黑。
 */
class SettingsActivity : Activity() {

    private lateinit var root: View
    private lateinit var blurBg: ImageView
    private lateinit var tintLayer: View
    private lateinit var chipsBox: LinearLayout

    private var ax = -1f
    private var ay = -1f
    private var aw = 0
    private var ah = 0
    private var advanced = false
    private var closing = false
    private var entered = false

    private val zoomValues = intArrayOf(85, 100, 115, 130)
    private val zoomLabels = arrayOf("小", "标准", "大", "特大")

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        overridePendingTransition(0, 0)
        setContentView(R.layout.activity_settings)
        window.setFormat(PixelFormat.TRANSLUCENT)

        root = findViewById(R.id.root)
        blurBg = findViewById(R.id.blurBg)
        tintLayer = findViewById(R.id.tintLayer)
        chipsBox = findViewById(R.id.zoomChips)

        advanced = intent?.getBooleanExtra(EXTRA_ADVANCED, false) ?: false
        ax = intent?.getFloatExtra(EXTRA_AX, -1f) ?: -1f
        ay = intent?.getFloatExtra(EXTRA_AY, -1f) ?: -1f
        aw = intent?.getIntExtra(EXTRA_AW, 0) ?: 0
        ah = intent?.getIntExtra(EXTRA_AH, 0) ?: 0

        setupGlass()
        placeWindow()
        bindRows()
        buildZoomChips()

        findViewById<TextView>(R.id.closeBtn).setOnClickListener { closePanel() }
        // 窗口是 floating 的，点外面直接结束——不需要自己补一层全屏暗幕
        setFinishOnTouchOutside(true)

        root.scaleX = 0.96f
        root.scaleY = 0.96f
        root.alpha = 0f
        root.translationY = -dp(this, 8).toFloat()

        root.post {
            if (!closing && !entered) playEnter()
        }
    }

    /** 真模糊优先；截不到就退成半透明深玻璃。 */
    private fun setupGlass() {
        val blurred: Bitmap? = SettingsBackdrop.blurred
        if (blurred != null) {
            blurBg.setImageBitmap(blurred)
            blurBg.visibility = View.VISIBLE
            tintLayer.setBackgroundColor(0x7A11161E.toInt())
        } else {
            blurBg.visibility = View.GONE
            tintLayer.setBackgroundColor(0xC8181B22.toInt())
        }

        // 12+ 再叠一层系统 blur-behind：窗外的网页一起虚化，边缘更自然
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            runCatching {
                window.addFlags(WindowManager.LayoutParams.FLAG_BLUR_BEHIND)
                val attrs = window.attributes
                attrs.blurBehindRadius = dp(this, 20)
                window.attributes = attrs
            }
        }
    }

    /**
     * 关键：把**窗口本身**定成一块小浮窗。
     * 宽度 = min(244dp, 屏宽 * 0.62)，高度随内容；贴屏幕右上，向下挂在胶囊下面。
     */
    private fun placeWindow() {
        val dm = resources.displayMetrics
        val widthPx = min(dp(this, 244), (dm.widthPixels * 0.62f).toInt())
        window.setLayout(widthPx, ViewGroup.LayoutParams.WRAP_CONTENT)
        window.setGravity(Gravity.TOP or Gravity.END)

        val margin = dp(this, 10)
        val lp = window.attributes
        lp.horizontalMargin = 0f
        lp.verticalMargin = 0f
        // gravity 是 END，x 取负值 = 向左缩，即右边距
        lp.x = -margin
        lp.y = if (ay >= 0f) (ay + ah).toInt() + dp(this, 7) else dp(this, 58)
        window.attributes = lp

        // 模糊图必须**对齐**到浮层所在的那块画面，否则就是把整屏压成一张小图，看着像贴了张照片
        val popupLeft = dm.widthPixels - margin - widthPx
        val popupTop = lp.y
        blurBg.imageMatrix = android.graphics.Matrix().apply {
            setTranslate(-popupLeft.toFloat(), -popupTop.toFloat())
        }
    }

    private fun playEnter() {
        entered = true
        root.animate()
            .scaleX(1f).scaleY(1f).alpha(1f).translationY(0f)
            .setDuration(190)
            .setInterpolator(DecelerateInterpolator(1.6f))
            .start()
    }

    private fun closePanel() = closePanel(null)

    private fun closePanel(then: (() -> Unit)?) {
        if (closing) return
        closing = true
        root.animate()
            .scaleX(0.97f).scaleY(0.97f).alpha(0f)
            .translationY(-dp(this, 6).toFloat())
            .setDuration(140)
            .setInterpolator(DecelerateInterpolator(1.4f))
            .withEndAction {
                then?.invoke()
                finish()
                overridePendingTransition(0, 0)
            }
            .start()
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
        // 右侧直接显示当前档位，把"右边空一大块"填住
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
            findViewById<View>(R.id.rowCopy).findViewById<View>(R.id.row_divider).visibility = View.GONE
        } else {
            // 高级项隐藏时，最后一行也不要顶着圆角画分隔线
            findViewById<View>(R.id.rowUpdate).findViewById<View>(R.id.row_divider).visibility = View.GONE
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
        val row = findViewById<View>(id)
        row.findViewById<TextView>(R.id.row_title).text = title
        row.findViewById<ImageView>(R.id.row_icon).apply {
            setImageResource(icon)
            setColorFilter(tint)
        }
        val rightView = row.findViewById<TextView>(R.id.row_right)
        if (right.isBlank()) {
            rightView.visibility = View.GONE
        } else {
            rightView.text = right
            rightView.visibility = View.VISIBLE
        }
        row.setOnClickListener { onClick() }
    }

    private fun toggleZoomChips() {
        if (chipsBox.visibility == View.VISIBLE) {
            chipsBox.visibility = View.GONE
        } else {
            buildZoomChips()
            chipsBox.visibility = View.VISIBLE
        }
    }

    /** 字号四档做成并排 chip，点一下立刻生效，浮层不关。 */
    private fun buildZoomChips() {
        chipsBox.removeAllViews()
        val current = SettingsBridge.zoom()
        zoomValues.forEachIndexed { i, v ->
            val chip = TextView(this)
            chip.text = zoomLabels[i]
            chip.textSize = 11f
            chip.gravity = Gravity.CENTER
            chip.setPadding(dp(this, 2), dp(this, 7), dp(this, 2), dp(this, 7))
            chip.background = getDrawable(
                if (v == current) R.drawable.bg_chip_on else R.drawable.bg_chip_off
            )
            chip.setTextColor(if (v == current) MINT else 0xFFB4C0D4.toInt())
            val lp = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
            lp.leftMargin = dp(this, 2)
            lp.rightMargin = dp(this, 2)
            chip.layoutParams = lp
            chip.setOnClickListener {
                SettingsBridge.act(ACT_ZOOM, v)
                buildZoomChips()
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
 * 设置浮层与 MainActivity 之间的单向桥。
 * 浮层是独立 Activity，要动的 WebView / prefs 都在 MainActivity 里，直接回调最省事。
 */
object SettingsBridge {
    @Volatile
    var host: MainActivity? = null

    fun act(action: String, arg: Int = 0) {
        host?.onSettingsAction(action, arg)
    }

    fun zoom(): Int = host?.currentZoom() ?: 100
}
