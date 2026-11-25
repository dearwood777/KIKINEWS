package com.kiki.horizonbrief

import android.app.job.JobInfo
import android.app.job.JobParameters
import android.app.job.JobScheduler
import android.app.job.JobService
import android.content.BroadcastReceiver
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.util.Log

/**
 * 小组件的「真正刷新」入口。
 *
 * 为什么要有这个类：组件原来只靠 appwidget-provider 里的 updatePeriodMillis 触发
 * onUpdate，而那条通路在国产 ROM 上极不可靠——后台限制一开，APPWIDGET_UPDATE 广播
 * 根本投递不到，组件就永远停在第一次添加时的那一版数据上（用户实测：11-23 装上，
 * 到 11-25 一直是 23 号的新闻）。设置页的「保存」更是只重绘缓存，压根不联网，
 * 所以点它也不可能变。
 *
 * 这里补三条互相独立的刷新通路：
 *   1) JobScheduler 周期任务（走系统 JobScheduler，比广播稳，且要求有网才跑）；
 *   2) 开机后重新注册一次任务；
 *   3) 打开 App 时、以及设置页点「立即刷新」时，直接联网拉一次再重绘。
 */
object WidgetRefresh {

    private const val TAG = "KikiWidget"
    private const val JOB_ID = 4201

    /** 周期任务间隔。日报一天一更，3 小时已经足够密，且不至于耗电。 */
    private const val INTERVAL_MS = 3L * 60 * 60 * 1000

    /** 打开 App 时如果距上次成功拉取不足这个时长，就不重复请求。 */
    const val FRESH_WINDOW_MS = 15L * 60 * 1000

    /** 注册（或更新）周期任务。幂等，重复调用只是覆盖同一条任务。 */
    fun schedule(context: Context) {
        val js = context.getSystemService(Context.JOB_SCHEDULER_SERVICE) as? JobScheduler ?: return
        val info = JobInfo.Builder(JOB_ID, ComponentName(context, WidgetRefreshJob::class.java))
            .setRequiredNetworkType(JobInfo.NETWORK_TYPE_ANY)
            .setPersisted(true)
            .setPeriodic(INTERVAL_MS)
            .build()
        runCatching { js.schedule(info) }
            .onFailure { Log.w(TAG, "schedule failed: ${it.message}") }
    }

    /**
     * 立刻联网拉一次，然后重绘所有组件。返回是否真的取到了新数据。
     * 会阻塞当前线程（网络 2~3 个源 × 4 秒上限），调用方自己放后台线程。
     */
    fun now(context: Context): Boolean {
        val fresh = runCatching { WidgetStore.refresh(context, maxAttempts = 3) }.getOrNull()
        runCatching { WidgetUpdater.refreshAll(context) }
            .onFailure { Log.w(TAG, "repaint failed: ${it.message}") }
        Log.i(TAG, "refresh now -> ${if (fresh == null) "failed, kept cache" else "ok ${fresh.date} ${fresh.updated}"}")
        return fresh != null
    }

    /** 打开 App 时用：数据已经很新就不再打网络，避免每次切前台都发请求。 */
    fun refreshIfStale(context: Context) {
        val age = System.currentTimeMillis() - WidgetStore.fetchedAt(context)
        if (age in 0 until FRESH_WINDOW_MS) return
        Thread {
            runCatching { now(context) }
        }.start()
    }

    fun fetchedAt(context: Context): Long = WidgetStore.fetchedAt(context)
}

/** 周期任务本体：JobScheduler 调起来后拉数据并重绘。 */
class WidgetRefreshJob : JobService() {

    override fun onStartJob(params: JobParameters?): Boolean {
        val ctx = applicationContext
        Thread {
            runCatching { WidgetRefresh.now(ctx) }
            // 失败也返回 false，不重试——下一个周期会再来，避免无限重试打爆电量
            jobFinished(params, false)
        }.start()
        return true
    }

    override fun onStopJob(params: JobParameters?): Boolean = false
}

/**
 * 开机后重新注册周期任务。
 *
 * JobScheduler 的 setPersisted(true) 理论上能跨重启，但部分国产 ROM 会清掉，
 * 多挂一个开机广播成本几乎为零，能兜住这种机型。
 */
class KikiBootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != Intent.ACTION_BOOT_COMPLETED) return
        WidgetRefresh.schedule(context)
        // 关机期间可能过了好几个早晨，顺手拉一次
        WidgetRefresh.refreshIfStale(context)
    }
}
