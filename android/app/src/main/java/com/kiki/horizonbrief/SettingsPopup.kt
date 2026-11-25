package com.kiki.horizonbrief

import android.graphics.Bitmap
import android.graphics.Color
import android.graphics.Matrix
import android.graphics.drawable.ColorDrawable
import android.view.Gravity
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.animation.DecelerateInterpolator
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.PopupWindow
import android.widget.TextView
import kotlin.math.min

/**
 * 设置浮层 —— **PopupWindow**，不是 Activity。
 *
 * 为什么彻底换掉 Activity 方案（用户连续否决 v1.6.013 / 014 / 015 三次"还是全屏"）：
 *   Activity 的窗口尺寸受主题、windowIsFloating、Dialog 最小宽度、ROM 定制等一堆因素影响，
 *   任何一个没吃准就退化成"整屏窗口里塞一块面板"，观感就是全屏。
 *   PopupWindow 的宽高由调用方**显式给定 px**，并且永远只占屏幕上那一小块，
 *   物理上不存在"铺满"的可能 —— 这是唯一不会翻车的形态。
 *
 * 尺寸：宽 = min(236dp, 屏宽 66%)，高 = wrap_content（约 230dp）。
 * 位置：挂在「设置」胶囊正下方 6dp，右边缘与胶囊对齐。
 * 玻璃：底色 [SettingsBackdrop] 的模糊截图，按浮层在屏幕上的真实位置做矩阵对齐，
 *      所以看到的是"浮层正下方那块网页被虚化"，不是一张缩略图。
 */
object SettingsPopup {

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

    private val zoomValues = intArrayOf(85, 100, 115, 130)
    private val zoomLabels = arrayOf("小", "标准", "大", "特大")

    private var pw: PopupWindow? = null
    private var hostRef: MainActivity? = null

    fun isShowing(): Boolean = pw?.isShowing == true

    /** 外部（MainActivity 失焦 / 返回键）调用：直接关掉，不执行任何动作。 */
    fun dismissNow() {
        val p = pw
        pw = null
        hostRef = null
        runCatching { p?.dismiss() }
    }

    fun show(host: MainActivity, anchor: View, advanced: Boolean) {
        dismissNow()
        val ctx = host
        val content = LayoutInflater.from(ctx).inflate(R.layout.activity_settings, null)

        val dm = ctx.resources.displayMetrics
        val widthPx = min(dp(ctx, 236), (dm.widthPixels * 0.66f).toInt())

        val popup = PopupWindow(content, widthPx, ViewGroup.LayoutParams.WRAP_CONTENT, false).apply {
            isOutsideTouchable = true
            isFocusable = true
            isClippingEnabled = true
            elevation = dp(ctx, 12).toFloat()
            // 必须给一个非 null 背景，否则 isOutsideTouchable 不生效（1/255 透明，肉眼看不见）
            setBackgroundDrawable(ColorDrawable(0x01000000))
        }

        pw = popup
        hostRef = host

        val blur = content.findViewById<ImageView>(R.id.blurBg)
        val tint = content.findViewById<View>(R.id.tintLayer)
        val chipsBox = content.findViewById<LinearLayout>(R.id.zoomChips)

        // 玻璃底
        val blurred: Bitmap? = SettingsBackdrop.blurred
        if (blurred != null) {
            blur.setImageBitmap(blurred)
            blur.visibility = View.VISIBLE
            tint.setBackgroundColor(0x7A11161E.toInt())
        } else {
            blur.visibility = View.GONE
            tint.setBackgroundColor(0xC8181B22.toInt())
        }

        bindRows(host, content, advanced, chipsBox)

        content.findViewById<TextView>(R.id.closeBtn).setOnClickListener { close(ctx, null) }

        // 入场：先把状态压小，显示后再放
        content.scaleX = 0.96f
        content.scaleY = 0.96f
        content.alpha = 0f
        content.translationY = -dp(ctx, 6).toFloat()

        val xoff = anchor.width - widthPx
        val yoff = dp(ctx, 6)
        runCatching {
            popup.showAsDropDown(anchor, xoff, yoff)
        }.onFailure {
            dismissNow()
            return
        }

        content.post {
            // 真实落点可能被系统夹到屏幕内，所以用实际位置对齐模糊图，保证"玻璃下面是这块画面"
            val loc = IntArray(2)
            content.getLocationOnScreen(loc)
            if (blurred != null) {
                blur.imageMatrix = Matrix().apply {
                    setTranslate(-loc[0].toFloat(), -loc[1].toFloat())
                }
            }
            content.animate()
                .scaleX(1f).scaleY(1f).alpha(1f).translationY(0f)
                .setDuration(170)
                .setInterpolator(DecelerateInterpolator(1.6f))
                .start()
        }
    }

    private fun close(host: MainActivity?, action: String?) {
        val p = pw ?: return
        pw = null
        hostRef = null
        val v = p.contentView
        v.animate()
            .scaleX(0.97f).scaleY(0.97f).alpha(0f)
            .setDuration(120)
            .withEndAction {
                runCatching { p.dismiss() }
                if (action != null && host != null) host.onSettingsAction(action)
            }
            .start()
    }

    private fun bindRows(
        host: MainActivity,
        root: View,
        advanced: Boolean,
        chipsBox: LinearLayout
    ) {
        val version = runCatching {
            host.packageManager.getPackageInfo(host.packageName, 0).versionName
        }.getOrNull() ?: ""
        root.findViewById<TextView>(R.id.panelTitle).text = "设置"

        bindRow(host, root, R.id.rowReload, "重新加载", R.drawable.ic_kv_refresh, CYAN, "") {
            close(host, ACT_RELOAD)
        }
        bindRow(host, root, R.id.rowHard, "强制刷新", R.drawable.ic_kv_clear, MINT, "清缓存") {
            close(host, ACT_HARD_RELOAD)
        }
        bindRow(host, root, R.id.rowTop, "回到顶部", R.drawable.ic_kv_top, BLUE, "") {
            close(host, ACT_TOP)
        }
        bindRow(host, root, R.id.rowZoom, "正文字号", R.drawable.ic_kv_text, CYAN, "${host.currentZoom()}%") {
            toggleChips(host, root, chipsBox)
        }
        bindRow(host, root, R.id.rowUpdate, "检查更新", R.drawable.ic_kv_update, AMBER, "v$version") {
            close(host, ACT_UPDATE)
        }

        val advViews = listOf(R.id.advGap, R.id.rowBrowser, R.id.rowCopy)
        advViews.forEach {
            root.findViewById<View>(it).visibility = if (advanced) View.VISIBLE else View.GONE
        }
        if (advanced) {
            bindRow(host, root, R.id.rowBrowser, "浏览器打开", R.drawable.ic_kv_browser, BLUE, "") {
                close(host, ACT_BROWSER)
            }
            bindRow(host, root, R.id.rowCopy, "复制链接", R.drawable.ic_kv_copy, MUTED, "") {
                close(host, ACT_COPY)
            }
            root.findViewById<View>(R.id.rowCopy).findViewById<View>(R.id.row_divider).visibility = View.GONE
        } else {
            root.findViewById<View>(R.id.rowUpdate).findViewById<View>(R.id.row_divider).visibility = View.GONE
        }
    }

    private fun bindRow(
        host: MainActivity,
        parent: View,
        id: Int,
        title: String,
        icon: Int,
        tint: Int,
        right: String,
        onClick: () -> Unit
    ) {
        val row = parent.findViewById<View>(id)
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

    private fun toggleChips(host: MainActivity, root: View, chipsBox: LinearLayout) {
        if (chipsBox.visibility == View.VISIBLE) {
            chipsBox.visibility = View.GONE
        } else {
            buildChips(host, root, chipsBox)
            chipsBox.visibility = View.VISIBLE
        }
    }

    private fun buildChips(host: MainActivity, root: View, chipsBox: LinearLayout) {
        chipsBox.removeAllViews()
        val current = host.currentZoom()
        zoomValues.forEachIndexed { i, v ->
            val chip = TextView(host)
            chip.text = zoomLabels[i]
            chip.textSize = 11f
            chip.gravity = Gravity.CENTER
            chip.setPadding(dp(host, 2), dp(host, 7), dp(host, 2), dp(host, 7))
            chip.background = host.getDrawable(
                if (v == current) R.drawable.bg_chip_on else R.drawable.bg_chip_off
            )
            chip.setTextColor(if (v == current) MINT else 0xFFB4C0D4.toInt())
            val lp = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
            lp.leftMargin = dp(host, 2)
            lp.rightMargin = dp(host, 2)
            chip.layoutParams = lp
            chip.setOnClickListener {
                host.onSettingsAction(ACT_ZOOM, v)
                buildChips(host, root, chipsBox)
                root.findViewById<View>(R.id.rowZoom)
                    .findViewById<TextView>(R.id.row_right).text = "$v%"
            }
            chipsBox.addView(chip)
        }
    }

    private fun dp(ctx: android.content.Context, v: Int): Int =
        (ctx.resources.displayMetrics.density * v).toInt()
}
