package com.kiki.horizonbrief

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.util.Log
import android.widget.RemoteViews
import org.json.JSONArray
import org.json.JSONObject
import java.io.BufferedReader
import java.net.HttpURLConnection
import java.net.URL

/**
 * 桌面小组件：4×1 与 4×2 两个独立条目，共用一套数据层与渲染层。
 *
 * 两者都走「集合型」组件（ListView + RemoteViewsService，见 WidgetService.kt）：
 * 行数由系统按真实高度决定，装得下几条就显示几条，超出部分可滚动。所以
 * 平板上不会「只给三条、底下空一大片」，手机上也不会「第三行只露半行」，
 * 更不需要任何「猜行数」的算法。
 *
 * 4×1 用紧凑版（头部 14dp、行高 22dp），40dp 的手机格子也能放「头部 + 一条」；
 * 4×2 用常规版（头部 20dp、行高 26/30dp）。
 *
 * 透明度：0–100%、10% 一档，11 个预制背景，点组件上的 ⚙ 调整。
 * 翻页：‹ › 跳一屏（步长 baseSlots），系统 30 分钟刷新时自动跳一屏；列表本身也能滑。
 * 数据来自 GitHub Pages 上的 widget.json，取不到退回本地缓存，再退回安装包内快照。
 */
open class KikiWidgetProvider : AppWidgetProvider() {

    /** 翻页步长。 */
    open val baseSlots: Int get() = 3

    /** 是否用紧凑版布局（4×1 为 true）。 */
    open val compact: Boolean get() = false

    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray
    ) {
        // 顺手把周期任务挂上：广播本身在国产 ROM 上经常投递不到，JobScheduler 是第二道保险
        WidgetRefresh.schedule(context)

        // 广播只有 10 秒窗口，网络尝试限制为两次、每次 3 秒超时
        val pending = goAsync()
        Thread {
            try {
                val fresh = WidgetStore.refresh(context, maxAttempts = 2)
                val feed = fresh ?: WidgetStore.cached(context)
                appWidgetIds.forEach { id ->
                    WidgetRenderer.render(
                        context, appWidgetManager, id, feed, step = 1,
                        providerClass = javaClass, baseSlots = baseSlots, compact = compact
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
        // 尺寸变了：列表型组件由系统自己重排，这里只刷新头部与数据，不动页码
        WidgetRenderer.render(
            context, appWidgetManager, appWidgetId, WidgetStore.cached(context), step = 0,
            providerClass = javaClass, baseSlots = baseSlots, compact = compact
        )
    }

    override fun onReceive(context: Context, intent: Intent) {
        super.onReceive(context, intent)
        val action = intent.action ?: return
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
            baseSlots = baseSlots,
            compact = compact
        )
    }

    override fun onDeleted(context: Context, appWidgetIds: IntArray) {
        appWidgetIds.forEach { WidgetStore.forget(context, it) }
    }

    companion object {
        private const val TAG = "KikiWidget"
        const val ACTION_NEXT = "com.kiki.horizonbrief.WIDGET_NEXT"
        const val ACTION_PREV = "com.kiki.horizonbrief.WIDGET_PREV"
    }
}

/** 4×1：picker 里单独一条，紧凑列表。 */
class KikiWidgetProvider4x1 : KikiWidgetProvider() {
    override val compact: Boolean get() = true
}

/** 4×2：picker 里单独一条，常规列表。 */
class KikiWidgetProvider4x2 : KikiWidgetProvider()

/** 透明度改完、或其他需要整体重绘时用。 */
object WidgetUpdater {
    fun refreshAll(context: Context) {
        val mgr = AppWidgetManager.getInstance(context)
        val providers = listOf(
            KikiWidgetProvider4x1::class.java to true,
            KikiWidgetProvider4x2::class.java to false
        )
        providers.forEach { (cls, compact) ->
            val ids = mgr.getAppWidgetIds(android.content.ComponentName(context, cls)) ?: return@forEach
            ids.forEach { id ->
                WidgetRenderer.render(
                    context, mgr, id, WidgetStore.cached(context), step = 0,
                    providerClass = cls, baseSlots = 3, compact = compact
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

    /**
     * 背景不透明度，0–100；默认 90。
     *
     * 按组件 id 分开存：桌面上同时放 4×1 和 4×2 时，两个组件各调各的，
     * 不会「最后改的那个把另一个也覆盖掉」。id 无效时退回全局默认值。
     */
    fun alpha(context: Context, id: Int): Int {
        val prefs = context.getSharedPreferences(PREF, Context.MODE_PRIVATE)
        return if (id == AppWidgetManager.INVALID_APPWIDGET_ID) {
            prefs.getInt(KEY_ALPHA, 90).coerceIn(0, 100)
        } else {
            prefs.getInt("alpha_$id", prefs.getInt(KEY_ALPHA, 90)).coerceIn(0, 100)
        }
    }

    fun setAlpha(context: Context, id: Int, pct: Int) {
        val prefs = context.getSharedPreferences(PREF, Context.MODE_PRIVATE).edit()
        if (id == AppWidgetManager.INVALID_APPWIDGET_ID) {
            prefs.putInt(KEY_ALPHA, pct.coerceIn(0, 100))
        } else {
            prefs.putInt("alpha_$id", pct.coerceIn(0, 100))
        }
        prefs.apply()
    }

    /** 免翻墙的取数顺序：GitHub Pages 同域 → jsDelivr 镜像 → ghfast 代理。 */
    private val SOURCES = listOf(
        "https://dearwood777.github.io/KIKINEWS/widget.json",
        "https://fastly.jsdelivr.net/gh/dearwood777/KIKINEWS@gh-pages/widget.json",
        "https://ghfast.top/https://raw.githubusercontent.com/dearwood777/KIKINEWS/gh-pages/widget.json",
    )

    /** 上一次成功联网的时间（毫秒），0 表示从没成功过。 */
    fun fetchedAt(context: Context): Long =
        context.getSharedPreferences(PREF, Context.MODE_PRIVATE).getLong(KEY_AT, 0L)

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
            conn.inputStream.bufferedReader().use { reader ->
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
        context.getSharedPreferences(PREF, Context.MODE_PRIVATE).edit()
            .putInt("page_$id", start).apply()
    }

    fun markSeen(context: Context, id: Int) {
        context.getSharedPreferences(PREF, Context.MODE_PRIVATE).edit()
            .putBoolean("seen_$id", true).apply()
    }

    fun isSeen(context: Context, id: Int): Boolean =
        context.getSharedPreferences(PREF, Context.MODE_PRIVATE).getBoolean("seen_$id", false)

    fun forget(context: Context, id: Int) {
        context.getSharedPreferences(PREF, Context.MODE_PRIVATE).edit()
            .remove("page_$id").remove("seen_$id").remove("alpha_$id").apply()
    }
}

object WidgetRenderer {

    const val EMPTY_HINT = "打开 App 同步今日新闻"

    private val THUMB = intArrayOf(
        R.drawable.bg_widget_a000, R.drawable.bg_widget_a010, R.drawable.bg_widget_a020,
        R.drawable.bg_widget_a030, R.drawable.bg_widget_a040, R.drawable.bg_widget_a050,
        R.drawable.bg_widget_a060, R.drawable.bg_widget_a070, R.drawable.bg_widget_a080,
        R.drawable.bg_widget_a090, R.drawable.bg_widget_a100
    )

    fun render(
        context: Context,
        manager: AppWidgetManager,
        id: Int,
        feed: WidgetFeed?,
        step: Int,
        providerClass: Class<*>,
        baseSlots: Int,
        compact: Boolean
    ) {
        val tablet = context.resources.configuration.smallestScreenWidthDp >= 600

        if (feed == null || feed.items.isEmpty()) {
            val views = RemoteViews(
                context.packageName,
                if (tablet) R.layout.widget_card_wide_single else R.layout.widget_card_single
            )
            applyAlpha(context, views, id)
            renderEmpty(context, views, id)
            manager.updateAppWidget(id, views)
            return
        }

        val items = feed.items
        val total = items.size
        val pageSize = baseSlots.coerceAtLeast(1)

        var start = WidgetStore.start(context, id).coerceIn(0, total - 1)
        if (step != 0 && WidgetStore.isSeen(context, id)) {
            start = ((start + step * pageSize) % total + total) % total
        }
        start = start.coerceIn(0, total - 1)
        WidgetStore.setStart(context, id, start)
        WidgetStore.markSeen(context, id)

        val dateText = listOf(feed.date.takeLast(5), feed.updated)
            .filter { it.isNotBlank() }.joinToString(" ")

        renderList(context, manager, id, total, dateText, providerClass, tablet, compact)
    }

    /**
     * 头部固定，列表填满剩余高度。行数交给系统（ListView 按真实高度排），
     * 所以不再有「猜行数」这一步，平板也不会留空白。
     */
    private fun renderList(
        context: Context,
        manager: AppWidgetManager,
        id: Int,
        total: Int,
        dateText: String,
        providerClass: Class<*>,
        tablet: Boolean,
        compact: Boolean
    ) {
        val layout = when {
            compact && tablet -> R.layout.widget_list_compact_wide
            compact -> R.layout.widget_list_compact
            tablet -> R.layout.widget_list_wide
            else -> R.layout.widget_list
        }
        val views = RemoteViews(context.packageName, layout)
        applyAlpha(context, views, id)

        views.setTextViewText(R.id.w_date, dateText)
        views.setTextViewText(R.id.w_page, "$total 条")
        views.setTextViewText(android.R.id.empty, EMPTY_HINT)

        bindConfig(context, views, id, R.id.w_set)
        bindArrow(context, views, id, R.id.w_prev, KikiWidgetProvider.ACTION_PREV, 2, providerClass)
        bindArrow(context, views, id, R.id.w_next, KikiWidgetProvider.ACTION_NEXT, 3, providerClass)
        views.setOnClickPendingIntent(R.id.w_date, openApp(context, id, null, 1, mutable = false))

        views.setEmptyView(R.id.w_list, android.R.id.empty)
        views.setRemoteAdapter(
            R.id.w_list,
            Intent(context, WidgetService::class.java)
                .putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, id)
                .putExtra(WidgetService.EXTRA_COMPACT, compact)
        )
        // 列表项点击靠 fill-in intent 把锚点传进 MainActivity，模板必须允许合并 extras
        views.setPendingIntentTemplate(R.id.w_list, openApp(context, id, null, 9, mutable = true))

        manager.updateAppWidget(id, views)
        manager.notifyAppWidgetViewDataChanged(id, R.id.w_list)
    }

    /** 11 档预制背景，按 10% 取整切换。 */
    private fun applyAlpha(context: Context, views: RemoteViews, id: Int) {
        val pct = WidgetStore.alpha(context, id)
        views.setInt(R.id.w_root, "setBackgroundResource", THUMB[(pct / 10).coerceIn(0, 10)])
    }

    private fun renderEmpty(context: Context, views: RemoteViews, id: Int) {
        views.setViewVisibility(R.id.w_single, android.view.View.VISIBLE)
        views.setViewVisibility(R.id.w_multi, android.view.View.GONE)
        views.setTextViewText(R.id.w_stitle, EMPTY_HINT)
        views.setTextViewText(R.id.w_stime, "")
        views.setViewVisibility(R.id.w_sprev, android.view.View.GONE)
        views.setViewVisibility(R.id.w_snext, android.view.View.GONE)
        views.setOnClickPendingIntent(R.id.w_stitle, openApp(context, id, null, 4, mutable = false))
    }

    /**
     * 透明度设置页直接以 Activity PendingIntent 打开。
     * 早前版本是「广播 → startActivity」，Android 10 起后台启动 Activity 会被拦，
     * 部分机型点 ⚙ 没反应就是这个原因。
     */
    private fun bindConfig(
        context: Context,
        views: RemoteViews,
        id: Int,
        viewId: Int
    ) {
        val intent = Intent(context, WidgetConfigActivity::class.java)
            .putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, id)
            .setData(Uri.parse("kiki://widget/$id/config"))
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        views.setOnClickPendingIntent(
            viewId,
            PendingIntent.getActivity(
                context,
                requestCode(id, 5),
                intent,
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
        slot: Int,
        providerClass: Class<*>
    ) {
        val intent = Intent(context, providerClass)
            .setAction(action)
            .setData(Uri.parse("kiki://widget/$id/arrow/$slot"))
            .putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, id)
        views.setOnClickPendingIntent(
            viewId,
            PendingIntent.getBroadcast(
                context,
                requestCode(id, slot),
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
        )
    }

    private fun openApp(
        context: Context,
        id: Int,
        anchor: String?,
        slot: Int,
        mutable: Boolean
    ): PendingIntent {
        val intent = Intent(context, MainActivity::class.java).apply {
            data = Uri.parse("kiki://widget/$id/open/$slot")
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP
            if (!anchor.isNullOrBlank()) putExtra(MainActivity.EXTRA_ANCHOR, anchor)
        }
        val flags = PendingIntent.FLAG_UPDATE_CURRENT or when {
            mutable && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> PendingIntent.FLAG_MUTABLE
            mutable -> 0
            else -> PendingIntent.FLAG_IMMUTABLE
        }
        return PendingIntent.getActivity(context, requestCode(id, slot), intent, flags)
    }

    /** 每个组件实例一套 requestCode，避免多个组件的 PendingIntent 互相覆盖。 */
    private fun requestCode(id: Int, slot: Int): Int = (id and 0xFFFF) * 16 + slot
}
