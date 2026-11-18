package com.kiki.horizonbrief

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.Context
import android.content.Intent
import android.os.Build
import android.util.Log
import android.util.SizeF
import android.widget.RemoteViews
import org.json.JSONArray
import org.json.JSONObject
import java.io.BufferedReader
import java.net.HttpURLConnection
import java.net.URL

/**
 * 桌面小组件：4×1 与 4×2 两个独立条目，共用一套渲染逻辑。
 *
 * 尺寸适配（1.6.001 起，响应式布局）：
 *   1. picker 标签用 targetCellWidth/targetCellHeight 声明格子数（Android 12+），
 *      Android 11 及以下退回 minWidth。
 *   2. 不再自己猜高度。把「能放 1 行 / 2 行 … 8 行」的布局全部注册进
 *      RemoteViews(Map<SizeF, RemoteViews>)，由系统按组件真实尺寸挑能装下的最大一档，
 *      所以手机上不会「第三行被裁一半」，平板上也不会「只给三条、下面空一片」。
 *   3. 窄版（手机）行高 26dp、标题 12.5sp；宽版（平板，最小屏宽 ≥600dp）行高 30dp、
 *      标题 14.5sp。选窄还是宽由设备类别决定，不再由组件宽度猜，避免手机被误判成宽版。
 * 透明度：0–100%，11 档预制背景，点组件上的 ⚙ 调整。
 * 翻页：‹ › 手动翻一页（步长 = 该 provider 的默认条数），系统 30 分钟刷新自动翻一页。
 * 数据来自 GitHub Pages 上的 widget.json，取不到退回本地缓存，再退回安装包内快照。
 */
open class KikiWidgetProvider : AppWidgetProvider() {

    /** 翻一页走几条：4×1 给 1，4×2 给 3。 */
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
        // 用户拉了尺寸：响应式布局由系统重挑，这里只需按新尺寸重渲染一次，页码保持
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

/** 4×1：picker 里单独一条，手机上一条、平板上按高度自动多显示几条。 */
class KikiWidgetProvider4x1 : KikiWidgetProvider() {
    override val baseSlots: Int get() = 1
}

/** 4×2：picker 里单独一条，默认三条。 */
class KikiWidgetProvider4x2 : KikiWidgetProvider() {
    override val baseSlots: Int get() = 3
}

/** 透明度改完、或其他需要整体重绘时用。 */
object WidgetUpdater {
    fun refreshAll(context: Context) {
        val mgr = AppWidgetManager.getInstance(context)
        for (cls in listOf(KikiWidgetProvider4x1::class.java, KikiWidgetProvider4x2::class.java)) {
            val ids = mgr.getAppWidgetIds(android.content.ComponentName(context, cls)) ?: continue
            ids.forEach { id ->
                WidgetRenderer.render(
                    context, mgr, id, WidgetStore.cached(context), step = 0,
                    providerClass = cls,
                    baseSlots = if (cls == KikiWidgetProvider4x1::class.java) 1 else 3
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

    /** 背景不透明度，0–100；默认 90。 */
    fun alpha(context: Context): Int =
        context.getSharedPreferences(PREF, Context.MODE_PRIVATE)
            .getInt(KEY_ALPHA, 90).coerceIn(0, 100)

    fun setAlpha(context: Context, pct: Int) {
        context.getSharedPreferences(PREF, Context.MODE_PRIVATE).edit()
            .putInt(KEY_ALPHA, pct.coerceIn(0, 100)).apply()
    }

    /** 免翻墙的取数顺序：GitHub Pages 同域 → jsDelivr 镜像 → ghfast 代理。 */
    private val SOURCES = listOf(
        "https://dearwood777.github.io/KIKINEWS/widget.json",
        "https://fastly.jsdelivr.net/gh/dearwood777/KIKINEWS@gh-pages/widget.json",
        "https://ghfast.top/https://raw.githubusercontent.com/dearwood777/KIKINEWS/gh-pages/widget.json",
    )

    fun cached(context: Context): WidgetFeed? {
        val prefs = context.getSharedPreferences(PREF, Context.MODE_PRIVATE)
        val raw = prefs.getString(KEY_FEED, null)
        if (!raw.isNullOrBlank()) parse(raw)?.let { return it }
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

    /** page_<id> 存的是「当前首条在 items 里的下标」，不是页号。 */
    fun start(context: Context, id: Int): Int =
        context.getSharedPreferences(PREF, Context.MODE_PRIVATE).getInt("page_$id", 0)

    fun setStart(context: Context, id: Int, start: Int) {
        context.getSharedPreferences(PREF, Context.MODE_PRIVATE).edit().putInt("page_$id", start).apply()
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
 * 响应式渲染：
 * - 每种行数（1–8）都有对应布局，注册到 RemoteViews(SizeF → views)，系统按真实尺寸选；
 * - 每行固定高度，条目从「首条下标」开始循环取，永远填满可见行，不会出现半行。
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

    /** 窄版（手机）：行高 26dp、头部 20dp、上下内边距合计 10dp。 */
    private fun narrowLayout(rows: Int): Int = when (rows) {
        1 -> R.layout.widget_card_single
        2 -> R.layout.widget_card_r2
        3 -> R.layout.widget_card_r3
        4 -> R.layout.widget_card_r4
        5 -> R.layout.widget_card_r5
        6 -> R.layout.widget_card_r6
        7 -> R.layout.widget_card_r7
        else -> R.layout.widget_card_r8
    }

    /** 宽版（平板）：行高 30dp、头部 24dp、上下内边距合计 10dp。 */
    private fun wideLayout(rows: Int): Int = when (rows) {
        1 -> R.layout.widget_card_wide_single
        2 -> R.layout.widget_card_wide_r2
        3 -> R.layout.widget_card_wide_r3
        4 -> R.layout.widget_card_wide_r4
        5 -> R.layout.widget_card_wide_r5
        6 -> R.layout.widget_card_wide_r6
        7 -> R.layout.widget_card_wide_r7
        else -> R.layout.widget_card_wide_r8
    }

    fun render(
        context: Context,
        manager: AppWidgetManager,
        id: Int,
        feed: WidgetFeed?,
        step: Int,
        providerClass: Class<*>,
        baseSlots: Int
    ) {
        val tablet = context.resources.configuration.smallestScreenWidthDp >= 600

        if (feed == null || feed.items.isEmpty()) {
            val views = RemoteViews(context.packageName, narrowLayout(1))
            applyAlpha(context, views)
            renderEmpty(context, views, id)
            manager.updateAppWidget(id, views)
            return
        }

        val items = feed.items
        val total = items.size
        val pageSize = baseSlots.coerceAtLeast(1)
        val pages = (total + pageSize - 1) / pageSize

        var start = WidgetStore.start(context, id).coerceIn(0, total - 1)
        if (step != 0 && WidgetStore.isSeen(context, id)) {
            start = ((start + step * pageSize) % total + total) % total
        }
        start = start.coerceIn(0, total - 1)
        WidgetStore.setStart(context, id, start)
        WidgetStore.markSeen(context, id)

        val dateText = listOf(feed.date.takeLast(5), feed.updated)
            .filter { it.isNotBlank() }.joinToString(" ")

        val pageNo = start / pageSize + 1

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            val variants = HashMap<SizeF, RemoteViews>()
            for (rows in 1..MAX_ROWS) {
                val layout = if (tablet) wideLayout(rows) else narrowLayout(rows)
                val views = RemoteViews(context.packageName, layout)
                applyAlpha(context, views)
                fill(
                    context, views, rows, items, start, total, dateText,
                    pageNo, pages, id, providerClass
                )
                // 宽度给 1dp 表示「任何宽度都接受」，系统只按高度挑档；
                // 高度 = 头部 + 内边距 + 行数 × 行高
                val rowDp = if (tablet) 30 else 26
                val headDp = if (tablet) 24 else 20
                variants[SizeF(1f, (headDp + 10 + rows * rowDp).toFloat())] = views
            }
            manager.updateAppWidget(id, RemoteViews(variants))
        } else {
            // Android 11 及以下没有响应式布局，按高度下限估一档；行高固定，最多差一行
            val h = manager.getAppWidgetOptions(id)
                .getInt(AppWidgetManager.OPTION_APPWIDGET_MIN_HEIGHT, 0)
            val rowDp = if (tablet) 30 else 26
            val headDp = if (tablet) 24 else 20
            val rows = ((h - headDp - 10) / rowDp).coerceIn(1, MAX_ROWS)
            val layout = if (tablet) wideLayout(rows) else narrowLayout(rows)
            val views = RemoteViews(context.packageName, layout)
            applyAlpha(context, views)
            fill(
                context, views, rows, items, start, total, dateText,
                pageNo, pages, id, providerClass
            )
            manager.updateAppWidget(id, views)
        }
    }

    /** 把数据填进指定行数的布局：1 行走单行模式，2 行以上走列表模式。 */
    private fun fill(
        context: Context,
        views: RemoteViews,
        rows: Int,
        items: List<WidgetItem>,
        start: Int,
        total: Int,
        dateText: String,
        pageNo: Int,
        pages: Int,
        id: Int,
        providerClass: Class<*>
    ) {
        bindConfig(context, views, id, providerClass, R.id.w_set)
        bindConfig(context, views, id, providerClass, R.id.w_sset)

        if (rows <= 1) {
            views.setViewVisibility(R.id.w_single, android.view.View.VISIBLE)
            views.setViewVisibility(R.id.w_multi, android.view.View.GONE)
            val it = items[start % total]
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
            return
        }

        views.setViewVisibility(R.id.w_multi, android.view.View.VISIBLE)
        views.setViewVisibility(R.id.w_single, android.view.View.GONE)
        views.setTextViewText(R.id.w_date, dateText)
        views.setTextViewText(R.id.w_page, "$pageNo/$pages")
        bindArrow(context, views, id, R.id.w_prev, KikiWidgetProvider.ACTION_PREV, 20, providerClass)
        bindArrow(context, views, id, R.id.w_next, KikiWidgetProvider.ACTION_NEXT, 21, providerClass)
        views.setOnClickPendingIntent(R.id.w_date, openApp(context, id, null, 22))
        if (pages <= 1) {
            views.setViewVisibility(R.id.w_prev, android.view.View.GONE)
            views.setViewVisibility(R.id.w_next, android.view.View.GONE)
        }

        for (i in 0 until rows) {
            // 循环取：最后一页也不会留空行，永远填满可见行
            val item = items[(start + i) % total]
            views.setViewVisibility(ROW_IDS[i], android.view.View.VISIBLE)
            views.setTextViewText(TITLE_IDS[i], item.title)
            views.setTextViewText(SCORE_IDS[i], item.score)
            views.setOnClickPendingIntent(ROW_IDS[i], openApp(context, id, item.anchor, 30 + i))
        }
    }

    /** 11 档预制背景，按 10% 取整切换。 */
    private fun applyAlpha(context: Context, views: RemoteViews) {
        val pct = WidgetStore.alpha(context)
        views.setInt(R.id.w_root, "setBackgroundResource", THUMB[(pct / 10).coerceIn(0, 10)])
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
