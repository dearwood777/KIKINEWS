package com.kiki.horizonbrief

import android.app.Activity
import android.appwidget.AppWidgetManager
import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.SeekBar
import android.widget.TextView
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * 小组件透明度设置页。
 *
 * 两种入口：
 *   1. 组件右上角的 ⚙（广播 ACTION_CONFIG 打开）；
 *   2. 部分 launcher 的「长按组件 → 组件设置」会直接拉起本页（provider 里配了 configure）。
 * 只做一件事：把不透明度存进 SharedPreferences（0–100，10% 一档），然后重绘所有组件。
 */
class WidgetConfigActivity : Activity() {

    private val thumbs = intArrayOf(
        R.drawable.bg_widget_a000, R.drawable.bg_widget_a010, R.drawable.bg_widget_a020,
        R.drawable.bg_widget_a030, R.drawable.bg_widget_a040, R.drawable.bg_widget_a050,
        R.drawable.bg_widget_a060, R.drawable.bg_widget_a070, R.drawable.bg_widget_a080,
        R.drawable.bg_widget_a090, R.drawable.bg_widget_a100
    )

    private var widgetId = AppWidgetManager.INVALID_APPWIDGET_ID
    private var pct = 90

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_widget_config)

        widgetId = intent?.getIntExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, AppWidgetManager.INVALID_APPWIDGET_ID)
            ?: AppWidgetManager.INVALID_APPWIDGET_ID

        // 从 launcher 的「添加组件」流程进来时，先按取消返回，点了保存再改成 OK
        if (widgetId != AppWidgetManager.INVALID_APPWIDGET_ID) {
            setResult(RESULT_CANCELED, Intent().putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, widgetId))
        }

        pct = WidgetStore.alpha(this, widgetId)

        val preview = findViewById<android.view.View>(R.id.cfg_preview)
        val value = findViewById<TextView>(R.id.cfg_value)
        val seek = findViewById<SeekBar>(R.id.cfg_seek)

        fun paint(p: Int) {
            pct = p
            value.text = getString(R.string.widget_config_value, p)
            preview.setBackgroundResource(thumbs[(p / 10).coerceIn(0, 10)])
        }

        seek.progress = pct
        paint(pct)

        seek.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(sb: SeekBar?, progress: Int, fromUser: Boolean) {
                paint((progress / 10) * 10)
            }

            override fun onStartTrackingTouch(sb: SeekBar?) {}
            override fun onStopTrackingTouch(sb: SeekBar?) {}
        })

        findViewById<Button>(R.id.cfg_save).setOnClickListener {
            WidgetStore.setAlpha(this, widgetId, pct)
            WidgetUpdater.refreshAll(this)
            if (widgetId != AppWidgetManager.INVALID_APPWIDGET_ID) {
                setResult(RESULT_OK, Intent().putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, widgetId))
            }
            finish()
        }

        // 「保存并刷新组件」只是拿缓存重绘，不联网；组件长期停在旧日期时，
        // 光点它是不可能变的，所以这里单独给一个真的会发请求的按钮。
        val status = findViewById<TextView>(R.id.cfg_status)
        val refreshBtn = findViewById<Button>(R.id.cfg_refresh)
        status.text = syncText()

        refreshBtn.setOnClickListener {
            refreshBtn.isEnabled = false
            status.text = getString(R.string.widget_config_running)
            Thread {
                val ok = WidgetRefresh.now(applicationContext)
                val feed = WidgetStore.cached(applicationContext)
                runOnUiThread {
                    refreshBtn.isEnabled = true
                    status.text = if (ok) {
                        getString(
                            R.string.widget_config_ok,
                            listOf(feed?.date.orEmpty(), feed?.updated.orEmpty())
                                .filter { s -> s.isNotBlank() }
                                .joinToString(" ")
                        )
                    } else {
                        getString(R.string.widget_config_fail)
                    }
                    setResult(RESULT_OK, Intent().putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, widgetId))
                }
            }.start()
        }

        WidgetRefresh.schedule(this)
    }

    /** 「上次同步：MM-dd HH:mm」，从没成功过时给一句白话。 */
    private fun syncText(): String {
        val at = WidgetStore.fetchedAt(this)
        if (at <= 0L) return getString(R.string.widget_config_never)
        val fmt = SimpleDateFormat("MM-dd HH:mm", Locale.getDefault())
        return getString(R.string.widget_config_last, fmt.format(Date(at)))
    }
}
