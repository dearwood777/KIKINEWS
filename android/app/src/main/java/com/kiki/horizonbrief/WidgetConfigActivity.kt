package com.kiki.horizonbrief

import android.app.Activity
import android.appwidget.AppWidgetManager
import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.SeekBar
import android.widget.TextView

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

        pct = WidgetStore.alpha(this)

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
            WidgetStore.setAlpha(this, pct)
            WidgetUpdater.refreshAll(this)
            if (widgetId != AppWidgetManager.INVALID_APPWIDGET_ID) {
                setResult(RESULT_OK, Intent().putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, widgetId))
            }
            finish()
        }
    }
}
