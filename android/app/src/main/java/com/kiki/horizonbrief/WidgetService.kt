package com.kiki.horizonbrief

import android.appwidget.AppWidgetManager
import android.content.Context
import android.content.Intent
import android.widget.RemoteViews
import android.widget.RemoteViewsService

/**
 * 4×2 用的是「集合型」组件：ListView + RemoteViewsService。
 *
 * 为什么用它：普通 RemoteViews 拿不到组件真实高度，只能靠 launcher 回传的 dp 猜行数，
 * 而平板 launcher 回传的值明显偏小（只排 3 行、底下空三分之二）。ListView 由系统自己
 * 按真实高度布局，装得下几条显示几条，超出部分可以滚动，所以既不留空白、也不会裁半行，
 * 也不需要任何「猜行数」的算法。
 */
class WidgetService : RemoteViewsService() {
    override fun onGetViewFactory(intent: Intent): RemoteViewsFactory =
        WidgetFactory(
            applicationContext,
            intent.getIntExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, AppWidgetManager.INVALID_APPWIDGET_ID)
        )
}

class WidgetFactory(
    private val context: Context,
    private val widgetId: Int
) : RemoteViewsService.RemoteViewsFactory {

    private var items: List<WidgetItem> = emptyList()
    private var start = 0
    private var tablet = false

    override fun onCreate() {
        tablet = context.resources.configuration.smallestScreenWidthDp >= 600
    }

    override fun onDataSetChanged() {
        val feed = WidgetStore.cached(context) ?: return
        items = feed.items
        start = if (widgetId == AppWidgetManager.INVALID_APPWIDGET_ID) 0
        else WidgetStore.start(context, widgetId).coerceIn(0, maxOf(0, items.size - 1))
    }

    override fun onDestroy() {
        items = emptyList()
    }

    override fun getCount(): Int = items.size

    override fun getViewAt(position: Int): RemoteViews? {
        // position 是列表里的绝对位置；按「首条下标」循环，保证滚动到底也一直有内容
        val count = items.size
        if (count == 0) return null
        val item = items[(start + position) % count]
        val layout = if (tablet) R.layout.widget_row_wide else R.layout.widget_row
        val views = RemoteViews(context.packageName, layout)
        views.setTextViewText(R.id.w_row_t, item.title)
        views.setTextViewText(R.id.w_row_s, item.score)
        val fillIn = Intent().putExtra(MainActivity.EXTRA_ANCHOR, item.anchor)
        views.setOnClickFillInIntent(R.id.w_row, fillIn)
        return views
    }

    override fun getLoadingView(): RemoteViews? = null

    override fun getViewTypeCount(): Int = 1

    override fun getItemId(position: Int): Long = position.toLong()

    override fun hasStableIds(): Boolean = false
}
