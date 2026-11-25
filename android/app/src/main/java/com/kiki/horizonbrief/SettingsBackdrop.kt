package com.kiki.horizonbrief

import android.app.Activity
import android.graphics.Bitmap
import android.os.Build
import android.os.Handler
import android.os.Looper
import android.view.PixelCopy
import android.view.View
import kotlin.math.max
import kotlin.math.min

/**
 * 给设置浮层做「背后画面被虚化」的底图。
 *
 * Android 只有 12+ 才有系统级的 blur-behind，低版本拿不到真模糊；
 * 这里用 PixelCopy 把当前网页画面截下来，缩到 1/8 再用盒式模糊抹平，
 * 放回面板底层 —— 观感上和 iOS 的毛玻璃一致（背后内容在，但认不出细节）。
 * 截图失败（受保护图层 / 硬件渲染不给拷）就返回 null，面板退成半透明深色。
 */
object SettingsBackdrop {

    /** 上一次成功生成的模糊底图；面板直接读它，没生成过就是 null。 */
    @Volatile
    var blurred: Bitmap? = null

    private const val DOWNSCALE = 8
    private const val PASSES = 3
    private const val RADIUS = 4

    /**
     * 异步截图 + 模糊。无论成功失败都会调用 [onReady]，最多等 280ms，
     * 不会把「打开设置」这个交互卡住。
     */
    fun capture(activity: Activity, source: View, onReady: () -> Unit) {
        blurred = null
        val w = activity.window.decorView.width
        val h = activity.window.decorView.height
        if (w <= 0 || h <= 0 || Build.VERSION.SDK_INT < Build.VERSION_CODES.O) {
            onReady()
            return
        }
        val full = runCatching {
            Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888)
        }.getOrNull()
        if (full == null) {
            onReady()
            return
        }

        var done = false
        val main = Handler(Looper.getMainLooper())

        // 超时兜底：截图偶尔会迟迟不回调，不能让它拖住点击
        main.postDelayed({
            if (!done) {
                done = true
                onReady()
            }
        }, 280)

        val listener = PixelCopy.OnPixelCopyFinishedListener { result ->
            if (!done) {
                done = true
                if (result == PixelCopy.SUCCESS) {
                    blurred = runCatching { blur(full) }.getOrNull()
                }
                full.recycle()
                onReady()
            }
        }

        runCatching {
            PixelCopy.request(activity.window, full, listener, main)
        }.onFailure {
            if (!done) {
                done = true
                onReady()
            }
        }
    }

    /** 降采样 → 三趟盒式模糊（近似高斯），放大后看不出像素块。 */
    private fun blur(src: Bitmap): Bitmap {
        val w = max(1, src.width / DOWNSCALE)
        val h = max(1, src.height / DOWNSCALE)
        var bmp = Bitmap.createScaledBitmap(src, w, h, true)
        val pix = IntArray(w * h)
        bmp.getPixels(pix, 0, w, 0, 0, w, h)
        val tmp = IntArray(w * h)
        repeat(PASSES) {
            blurPass(pix, tmp, w, h, RADIUS, horizontal = true)
            blurPass(tmp, pix, w, h, RADIUS, horizontal = false)
        }
        bmp = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888)
        bmp.setPixels(pix, 0, w, 0, 0, w, h)
        return bmp
    }

    private fun blurPass(src: IntArray, dst: IntArray, w: Int, h: Int, r: Int, horizontal: Boolean) {
        val div = 2 * r + 1
        if (horizontal) {
            for (y in 0 until h) {
                val row = y * w
                var sa = 0; var sr = 0; var sg = 0; var sb = 0
                for (i in -r..r) {
                    val c = src[row + clamp(i, 0, w - 1)]
                    sa += c ushr 24 and 0xFF
                    sr += c ushr 16 and 0xFF
                    sg += c ushr 8 and 0xFF
                    sb += c and 0xFF
                }
                for (x in 0 until w) {
                    dst[row + x] = ((sa / div) shl 24) or ((sr / div) shl 16) or
                        ((sg / div) shl 8) or (sb / div)
                    val out = src[row + clamp(x - r, 0, w - 1)]
                    val inn = src[row + clamp(x + r + 1, 0, w - 1)]
                    sa += (inn ushr 24 and 0xFF) - (out ushr 24 and 0xFF)
                    sr += (inn ushr 16 and 0xFF) - (out ushr 16 and 0xFF)
                    sg += (inn ushr 8 and 0xFF) - (out ushr 8 and 0xFF)
                    sb += (inn and 0xFF) - (out and 0xFF)
                }
            }
        } else {
            for (x in 0 until w) {
                var sa = 0; var sr = 0; var sg = 0; var sb = 0
                for (i in -r..r) {
                    val c = src[clamp(i, 0, h - 1) * w + x]
                    sa += c ushr 24 and 0xFF
                    sr += c ushr 16 and 0xFF
                    sg += c ushr 8 and 0xFF
                    sb += c and 0xFF
                }
                for (y in 0 until h) {
                    dst[y * w + x] = ((sa / div) shl 24) or ((sr / div) shl 16) or
                        ((sg / div) shl 8) or (sb / div)
                    val out = src[clamp(y - r, 0, h - 1) * w + x]
                    val inn = src[clamp(y + r + 1, 0, h - 1) * w + x]
                    sa += (inn ushr 24 and 0xFF) - (out ushr 24 and 0xFF)
                    sr += (inn ushr 16 and 0xFF) - (out ushr 16 and 0xFF)
                    sg += (inn ushr 8 and 0xFF) - (out ushr 8 and 0xFF)
                    sb += (inn and 0xFF) - (out and 0xFF)
                }
            }
        }
    }

    private fun clamp(v: Int, lo: Int, hi: Int): Int = min(max(v, lo), hi)
}
