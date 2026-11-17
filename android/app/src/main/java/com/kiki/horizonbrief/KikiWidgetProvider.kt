package com.kiki.horizonbrief

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.Context
import android.content.Intent
import android.util.Log
import android.widget.RemoteViews
import org.json.JSONArray
import org.json.JSONObject
import java.io.BufferedReader
import java.net.HttpURLConnection
import java.net.URL

/**
 * 桌面小组件：4×1 与 4×2 两个独立条目，共用一套渲染逻辑。
 *
 * 尺寸适配（1.6.000 起）：
 *   1. widget_info_*.xml 用 targetCellWidth/targetCellHeight 按“格子”声明大小，
 *      手机和平板上 picker 都标 4×1 / 4×2（Android 12+；11 及以下退回 minWidth）。
 *   2. 布局里每一行是**固定行高**，能放几行由组件的真实高度算出来，放不下的行隐藏。
 *      所以把组件拉高只会多显示几条，不会再把行距撑开。
 *   3. 宽度 ≥300dp（平板）换用 widget_card_wide：行高 30dp、标题 14.5sp，
 *      手机上用 26dp / 12.5sp 的紧凑版。
 * 透明度：0–100%，11 档预制背景（bg_widget_a000…a100），点组件上的 ⚙ 调整。
 * 页内用 ‹ › 手动翻页，跟随系统 30 分钟刷新时自动翻一页。
 * 数据来自 GitHub Pages 上的 widget.json（约 2KB），取不到就退回本地缓存，
 * 再取不到就用安装包里内置的快照。
 */
open class KikiWidgetProvider : AppWidgetProvider() {

    /** 没拿到尺寸信息时至少显示几行：4×1 给 1，4×2 给 3。 */
    open val baseSlots: Int get() = 3

    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray
    ) {
        // 只给 10 秒窗口，网络失败的组合会超时，因此限制为两次尝试并各自 3 秒超时
        val pending = goAsync()
        Thread {
            try {
                val fresh = WidgetStore.refresh(context, maxAttempts = 2)
                val feed = fresh ?: WidgetStore.cached(context)
                appWidgetIds.forEach { id ->
                    WidgetRenderer.render(
                        context, appWidgetManager, id, feed, step = 1,
                        providerClass = javaClass, baseSlots = baseSlots
                    )
                }
            } catch (t: Throwable) {
                Log.w(TAG, "onUpdate failed: ${t.message}")
            } finally {
                pending.finish()
            }
        }.start()
    }

    override fun onAppWidgetOptionsChanged(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetId: Int,
        newOptions: android.os.Bundle
    ) {
        // 用户拉了尺寸，按新的高度重新决定显示几行，页码保持不变
        WidgetRenderer.render(
            context, appWidgetManager, appWidgetId, WidgetStore.cached(context), step = 0,
            providerClass = javaClass, baseSlots = baseSlots
        )
    }

    override fun onReceive(context: Context, intent: Intent) {
        super.onReceive(context, intent)
        val action = intent.action ?: return

        if (action == ACTION_CONFIG) {
            val id = intent.getIntExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, -1)
            if (id == -1) return
            context.startActivity(
                Intent(context, WidgetConfigActivity::class.java)
                    .putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, id)
                    .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            )
            return
        }

        if (action != ACTION_NEXT && action != ACTION_PREV) return
        val id = intent.getIntExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, -1)
        if (id == -1) return
        val mgr = AppWidgetManager.getInstance(context)
        WidgetRenderer.render(
            context,
            mgr,
            id,
            WidgetStore.cached(context),
            step = if (action == ACTION_NEXT) 1 else -1,
            providerClass = javaClass,
            baseSlots = baseSlots
        )
    }

    override fun onDeleted(context: Context, appWidgetIds: IntArray) {
        appWidgetIds.forEach { WidgetStore.forget(context, it) }
    }

    companion object {
        private const val TAG = "KikiWidget"
        const val ACTION_NEXT = "com.kiki.horizonbrief.WIDGET_NEXT"
        const val ACTION_PREV = "com.kiki.horizonbrief.WIDGET_PREV"
        const val ACTION_CONFIG = "com.kiki.horizonbrief.WIDGET_CONFIG"
    }
}

/** 4×1：picker 里单独一条，手机上一行、平板上会按高度自动多显示几条。 */
class KikiWidgetProvider4x1 : KikiWidgetProvider() {
    override val baseSlots: Int get() = 1
}

/** 4×2：picker 里单独一条，默认三条。 */
class KikiWidgetProvider4x2 : KikiWidgetProvider() {
    override val baseSlots: Int get() = 3
}

/** 组件面板里的统一刷新入口（透明度改完、或用户点了设置里的按钮）。 */
object WidgetUpdater {
    fun refreshAll(context: Context) {
        val mgr = AppWidgetManager.getInstance(context)
        for (cls in listOf(KikiWidgetProvider4x1::class.java, KikiWidgetProvider4x2::class.java)) {
            val ids = mgr.getAppWidgetIds(android.content.ComponentName(context, cls))
            ids?.forEach { id ->
                WidgetRenderer.render(
                    context, mgr, id, WidgetStore.cached(context), step = 0,
                    providerClass = cls, baseSlots = if (cls == KikiWidgetProvider4x1::class.java) 1 else 3
                )
            }
        }
    }
}

data class WidgetItem(val title: String, val score: String, val anchor: String, val sec: String)

data class WidgetFeed(val date: String, val updated: String, val items: List<WidgetItem>)

/** widget.json 的下载、缓存与解析。 */
object WidgetStore {

    private const val PREF = "widget"
    private const val KEY_FEED = "feed"
    private const val KEY_AT = "fetched_at"
    private const val KEY_ALPHA = "bg_alpha"

    /** 背景不透明度，0–100；默认 90（暗色但能透出一点壁纸）。 */
    fun alpha(context: Context): Int =
        context.getSharedPreferences(PREF, Context.MODE_PRIVATE)
            .getInt(KEY_ALPHA, 90).coerceIn(0, 100)

    fun setAlpha(context: Context, pct: Int) {
        context.getSharedPreferences(PREF, Context.MODE_PRIVATE).edit()
            .putInt(KEY_ALPHA, pct.coerceIn(0, 100)).apply()
    }

    /**
     * 免翻墙的取数顺序：先取 GitHub Pages 上的静态文件（和网页同一个域名，
     * 网页能打开这里就能打开），再退到两个国内可用的镜像/CDN。
     */
    private val SOURCES = listOf(
        "https://dearwood777.github.io/KIKINEWS/widget.json",
        "https://fastly.jsdelivr.net/gh/dearwood777/KIKINEWS@gh-pages/widget.json",
        "https://ghfast.top/https://raw.githubusercontent.com/dearwood777/KIKINEWS/gh-pages/widget.json",
    )

    fun cached(context: Context): WidgetFeed? {
        val prefs = context.getSharedPreferences(PREF, Context.MODE_PRIVATE)
        val raw = prefs.getString(KEY_FEED, null)
        if (!raw.isNullOrBlank()) parse(raw)?.let { return it }
        // 装完 App 还没联网时，用安装包里带的快照，至少不是一片空白
        return runCatching {
            context.assets.open("widget_cache.json").bufferedReader().use { it.readText() }
                .let { parse(it) }
        }.getOrNull()
    }

    /** 逐个源尝试，任意一个成功就落盘缓存并返回；全部失败返回 null。 */
    fun refresh(context: Context, maxAttempts: Int = 2): WidgetFeed? {
        for (url in SOURCES.take(maxAttempts)) {
            val body = fetch(url) ?: continue
            val feed = parse(body) ?: continue
            val prefs = context.getSharedPreferences(PREF, Context.MODE_PRIVATE)
            prefs.edit()
                .putString(KEY_FEED, body)
                .putLong(KEY_AT, System.currentTimeMillis())
                .apply()
            return feed
        }
        return null
    }

    private fun fetch(url: String): String? {
        var conn: HttpURLConnection? = null
        return try {
            conn = (URL(url).openConnection() as HttpURLConnection).apply {
                connectTimeout = 3000
                readTimeout = 3000
                requestMethod = "GET"
                instanceFollowRedirects = true
                setRequestProperty("User-Agent", "KIKINEWS-Widget/1.0")
                setRequestProperty("Cache-Control", "no-cache")
            }
            if (conn.responseCode != 200) return null
            BufferedReader(conn.inputStream.bufferedReader()).use { reader ->
                val sb = StringBuilder()
                var line = reader.readLine()
                while (line != null && sb.length < 64 * 1024) {
                    sb.append(line)
                    line = reader.readLine()
                }
                sb.toString()
            }
        } catch (t: Throwable) {
            Log.w("KikiWidget", "fetch failed $url: ${t.message}")
            null
        } finally {
            runCatching { conn?.disconnect() }
        }
    }

    private fun parse(raw: String): WidgetFeed? = runCatching {
        val root = JSONObject(raw)
        val arr: JSONArray = root.optJSONArray("items") ?: return null
        val items = (0 until arr.length()).mapNotNull { i ->
            val o = arr.optJSONObject(i) ?: return@mapNotNull null
            val title = o.optString("t").trim()
            if (title.isEmpty()) null
            else WidgetItem(
                title = title,
                score = o.optString("s"),
                anchor = o.optString("a"),
                sec = o.optString("sec")
            )
        }
        if (items.isEmpty()) null
        else WidgetFeed(
            date = root.optString("date"),
            updated = root.optString("updated"),
            items = items
        )
    }.getOrNull()

    fun page(context: Context, id: Int): Int =
        context.getSharedPreferences(PREF, Context.MODE_PRIVATE).getInt("page_$id", 0)

    fun setPage(context: Context, id: Int, page: Int) {
        context.getSharedPreferences(PREF, Context.MODE_PRIVATE).edit().putInt("page_$id", page).apply()
    }

    fun markSeen(context: Context, id: Int) {
        context.getSharedPreferences(PREF, Context.MODE_PRIVATE).edit().putBoolean("seen_$id", true).apply()
    }

    fun isSeen(context: Context, id: Int): Boolean =
        context.getSharedPreferences(PREF, Context.MODE_PRIVATE).getBoolean("seen_$id", false)

    fun forget(context: Context, id: Int) {
        context.getSharedPreferences(PREF, Context.MODE_PRIVATE).edit()
            .remove("page_$id").remove("seen_$id").apply()
    }
}

/**
 * 按组件真实尺寸选布局、算行数、填内容。
 * 行高是写死的（窄 26dp / 宽 30dp），所以高度变大只会多显示条目。
 */
object WidgetRenderer {

    private const val MAX_ROWS = 8
    const val EMPTY_HINT = "打开 App 同步今日新闻"

    private val THUMB = intArrayOf(
        R.drawable.bg_widget_a000, R.drawable.bg_widget_a010, R.drawable.bg_widget_a020,
        R.drawable.bg_widget_a030, R.drawable.bg_widget_a040, R.drawable.bg_widget_a050,
        R.drawable.bg_widget_a060, R.drawable.bg_widget_a070, R.drawable.bg_widget_a080,
        R.drawable.bg_widget_a090, R.drawable.bg_widget_a100
    )

    private val ROW_IDS = intArrayOf(
        R.id.w_r1, R.id.w_r2, R.id.w_r3, R.id.w_r4,
        R.id.w_r5, R.id.w_r6, R.id.w_r7, R.id.w_r8
    )
    private val TITLE_IDS = intArrayOf(
        R.id.w_t1, R.id.w_t2, R.id.w_t3, R.id.w_t4,
        R.id.w_t5, R.id.w_t6, R.id.w_t7, R.id.w_t8
    )
    private val SCORE_IDS = intArrayOf(
        R.id.w_s1, R.id.w_s2, R.id.w_s3, R.id.w_s4,
        R.id.w_s5, R.id.w_s6, R.id.w_s7, R.id.w_s8
    )

    fun render(
        context: Context,
        manager: AppWidgetManager,
        id: Int,
        feed: WidgetFeed?,
        step: Int,
        providerClass: Class<*>,
        baseSlots: Int
    ) {
        val opts = manager.getAppWidgetOptions(id)
        val widthDp = opts.getInt(AppWidgetManager.OPTION_APPWIDGET_MIN_WIDTH, 0)
        val wide = widthDp >= 300
        val layout = if (wide) R.layout.widget_card_wide else R.layout.widget_card

        val views = RemoteViews(context.packageName, layout)
        applyAlpha(context, views)

        val slots = slotsFor(context, opts, wide, baseSlots)

        if (feed == null || feed.items.isEmpty()) {
            renderEmpty(context, views, id)
            manager.updateAppWidget(id, views)
            return
        }
        val items = feed.items
        val total = items.size
        val pages = (total + slots - 1) / slots

        var page = WidgetStore.page(context, id)
        if (step != 0 && WidgetStore.isSeen(context, id)) {
            page = (page + step + pages) % pages
        }
        page = page.coerceIn(0, pages - 1)
        WidgetStore.setPage(context, id, page)
        WidgetStore.markSeen(context, id)

        val dateText = listOf(feed.date.takeLast(5), feed.updated)
            .filter { it.isNotBlank() }.joinToString(" ")

        bindConfig(context, views, id, providerClass, R.id.w_set)
        bindConfig(context, views, id, providerClass, R.id.w_sset)

        if (slots <= 1) {
            views.setViewVisibility(R.id.w_single, android.view.View.VISIBLE)
            views.setViewVisibility(R.id.w_multi, android.view.View.GONE)
            val it = items[page.coerceAtMost(total - 1)]
            views.setTextViewText(R.id.w_stitle, it.title)
            views.setTextViewText(R.id.w_stime, dateText)
            views.setOnClickPendingIntent(R.id.w_stitle, openApp(context, id, it.anchor, 10))
            views.setOnClickPendingIntent(R.id.w_stime, openApp(context, id, null, 11))
            bindArrow(context, views, id, R.id.w_sprev, KikiWidgetProvider.ACTION_PREV, 12, providerClass)
            bindArrow(context, views, id, R.id.w_snext, KikiWidgetProvider.ACTION_NEXT, 13, providerClass)
            if (pages <= 1) {
                views.setViewVisibility(R.id.w_sprev, android.view.View.GONE)
                views.setViewVisibility(R.id.w_snext, android.view.View.GONE)
            }
        } else {
            views.setViewVisibility(R.id.w_multi, android.view.View.VISIBLE)
            views.setViewVisibility(R.id.w_single, android.view.View.GONE)
            views.setTextViewText(R.id.w_date, dateText)
            views.setTextViewText(R.id.w_page, "${page + 1}/$pages")
            bindArrow(context, views, id, R.id.w_prev, KikiWidgetProvider.ACTION_PREV, 20, providerClass)
            bindArrow(context, views, id, R.id.w_next, KikiWidgetProvider.ACTION_NEXT, 21, providerClass)
            views.setOnClickPendingIntent(R.id.w_date, openApp(context, id, null, 22))
            if (pages <= 1) {
                views.setViewVisibility(R.id.w_prev, android.view.View.GONE)
                views.setViewVisibility(R.id.w_next, android.view.View.GONE)
            }

            for (i in 0 until MAX_ROWS) {
                val idx = page * slots + i
                if (i < slots && idx < total) {
                    val it = items[idx]
                    views.setViewVisibility(ROW_IDS[i], android.view.View.VISIBLE)
                    views.setTextViewText(TITLE_IDS[i], it.title)
                    views.setTextViewText(SCORE_IDS[i], it.score)
                    views.setOnClickPendingIntent(
                        ROW_IDS[i], openApp(context, id, it.anchor, 30 + i)
                    )
                } else {
                    views.setViewVisibility(ROW_IDS[i], android.view.View.GONE)
                }
            }
        }

        manager.updateAppWidget(id, views)
    }

    /** 11 档预制背景，按 10% 取整切换，避免每帧画位图（也避开 RemoteViews 的位图大小限制）。 */
    private fun applyAlpha(context: Context, views: RemoteViews) {
        val pct = WidgetStore.alpha(context)
        val index = (pct / 10).coerceIn(0, 10)
        views.setInt(R.id.w_root, "setBackgroundResource", THUMB[index])
    }

    /**
     * 行数 = 组件真实高度能放下几行（固定行高，绝不拉伸）。
     * OPTION_APPWIDGET_MIN_HEIGHT 是当前高度下限，取它最安全：宁可少一行，也不裁切。
     */
    private fun slotsFor(
        context: Context,
        opts: android.os.Bundle,
        wide: Boolean,
        baseSlots: Int
    ): Int {
        val h = opts.getInt(AppWidgetManager.OPTION_APPWIDGET_MIN_HEIGHT, 0)
        val rowDp = if (wide) 30 else 26
        val headDp = if (wide) 24 else 20
        val padDp = 10
        val fit = (h - headDp - padDp) / rowDp
        // 刚放到桌面时尺寸可能还没回传，用 provider 自带的 baseSlots 兜底
        return maxOf(fit, baseSlots).coerceIn(1, MAX_ROWS)
    }

    private fun renderEmpty(context: Context, views: RemoteViews, id: Int) {
        views.setViewVisibility(R.id.w_single, android.view.View.VISIBLE)
        views.setViewVisibility(R.id.w_multi, android.view.View.GONE)
        views.setTextViewText(R.id.w_stitle, EMPTY_HINT)
        views.setTextViewText(R.id.w_stime, "")
        views.setViewVisibility(R.id.w_sprev, android.view.View.GONE)
        views.setViewVisibility(R.id.w_snext, android.view.View.GONE)
        views.setOnClickPendingIntent(R.id.w_stitle, openApp(context, id, null, 40))
    }

    private fun bindConfig(
        context: Context,
        views: RemoteViews,
        id: Int,
        providerClass: Class<*>,
        viewId: Int
    ) {
        views.setOnClickPendingIntent(
            viewId, PendingIntent.getBroadcast(
                context,
                50,
                Intent(context, providerClass)
                    .setAction(KikiWidgetProvider.ACTION_CONFIG)
                    .putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, id),
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
        )
    }

    private fun bindArrow(
        context: Context,
        views: RemoteViews,
        id: Int,
        viewId: Int,
        action: String,
        requestCode: Int,
        providerClass: Class<*>
    ) {
        views.setOnClickPendingIntent(
            viewId, PendingIntent.getBroadcast(
                context,
                requestCode,
                Intent(context, providerClass)
                    .setAction(action)
                    .putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, id),
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
        )
    }

    private fun openApp(context: Context, id: Int, anchor: String?, requestCode: Int): PendingIntent {
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP
            if (!anchor.isNullOrBlank()) putExtra(MainActivity.EXTRA_ANCHOR, anchor)
        }
        return PendingIntent.getActivity(
            context,
            requestCode,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
    }
}
