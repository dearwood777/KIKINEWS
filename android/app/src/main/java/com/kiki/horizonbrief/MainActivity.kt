package com.kiki.horizonbrief

import android.annotation.SuppressLint
import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.graphics.Color
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.net.Uri
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.SystemClock
import android.view.Gravity
import android.view.MotionEvent
import android.view.View
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout

/**
 * 单页 WebView 壳：只负责展示 Horizon 生成的 GitHub Pages 日报。
 * 抓取、AI 打分、去重全部在 GitHub Actions 上完成，APK 里没有任何密钥。
 */
class MainActivity : AppCompatActivity() {

    private lateinit var web: WebView
    private lateinit var swipe: SwipeRefreshLayout
    private lateinit var errorPanel: View
    private lateinit var errorText: TextView
    private lateinit var prefs: SharedPreferences

    /** 长按设置按钮满 6 秒解锁高级项；计时器随手指抬起/取消清掉。 */
    private val holdHandler = Handler(Looper.getMainLooper())
    private var holdStartAt = 0L
    private var holdUnlocked = false
    /** 从桌面小组件点进来时带的锚点，页面加载完再滚动过去。 */
    private var pendingAnchor: String? = null
    private val unlockTask = Runnable {
        holdUnlocked = true
        toast("已解锁高级选项，松手后显示")
    }

    companion object {
        /** 第一次启动用的默认地址：本仓库的 GitHub Pages。 */
        private const val DEFAULT_URL =
            "https://dearwood777.github.io/KIKINEWS/latest.html"

        private const val PREF = "horizon"
        private const val KEY_URL = "digest_url"
        private const val KEY_ZOOM = "text_zoom"

        /** 桌面小组件点击标题时带过来的新闻锚点。 */
        const val EXTRA_ANCHOR = "anchor"

        /** 长按多久解锁「在浏览器中打开」「复制日报链接」。 */
        private const val HOLD_UNLOCK_MS = 6000L
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        enterImmersive()

        prefs = getSharedPreferences(PREF, Context.MODE_PRIVATE)
        web = findViewById(R.id.web)
        swipe = findViewById(R.id.swipe)
        errorPanel = findViewById(R.id.errorPanel)
        errorText = findViewById(R.id.errorText)

        setupWebView()

        pendingAnchor = intent?.getStringExtra(EXTRA_ANCHOR)

        swipe.setOnRefreshListener { load(digestUrl()) }
        findViewById<View>(R.id.retryButton).setOnClickListener {
            errorPanel.visibility = View.GONE
            load(digestUrl())
        }
        findViewById<View>(R.id.settingsButton).setOnTouchListener { v, ev ->
            handleSettingsTouch(v, ev)
        }

        load(digestUrl())

        // 每次启动静默查一次新版本（同一个版本只自动提示一次）
        UpdateChecker.check(this)
    }

    /** 沉浸式全屏：隐藏状态栏和导航栏，滑动边缘可临时唤出，松手后自动收起。 */
    @Suppress("DEPRECATION")
    private fun enterImmersive() {
        window.decorView.systemUiVisibility = (
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                or View.SYSTEM_UI_FLAG_FULLSCREEN
                or View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                or View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                or View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                or View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
            )
    }

    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        if (hasFocus) enterImmersive()
    }

    private fun digestUrl(): String = prefs.getString(KEY_URL, DEFAULT_URL) ?: DEFAULT_URL

    private fun digestHost(): String = Uri.parse(digestUrl()).host ?: ""

    @SuppressLint("SetJavaScriptEnabled")
    private fun setupWebView() {
        web.setBackgroundColor(Color.TRANSPARENT)
        web.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            cacheMode = WebSettings.LOAD_DEFAULT
            mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
            loadWithOverviewMode = true
            useWideViewPort = true
            builtInZoomControls = false
            textZoom = prefs.getInt(KEY_ZOOM, 100)
        }

        web.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(
                view: WebView,
                request: WebResourceRequest
            ): Boolean {
                val url = request.url
                // 站内链接留在 WebView，站外链接交给浏览器
                return if (url.host == digestHost()) {
                    false
                } else {
                    runCatching {
                        startActivity(Intent(Intent.ACTION_VIEW, url))
                    }.onFailure {
                        toast("没有可打开该链接的应用")
                    }
                    true
                }
            }

            override fun onPageFinished(view: WebView, url: String) {
                swipe.isRefreshing = false
                errorPanel.visibility = View.GONE
                scrollToPendingAnchor(view)
            }

            override fun onReceivedError(
                view: WebView,
                request: WebResourceRequest,
                error: WebResourceError
            ) {
                if (!request.isForMainFrame) return
                swipe.isRefreshing = false
                val reason = error.description?.toString().orEmpty()
                showError(reason)
            }
        }
    }

    /** 从小组件点标题进来：滚到那条新闻；找不到锚点就停在页首。 */
    private fun scrollToPendingAnchor(view: WebView) {
        val anchor = pendingAnchor ?: return
        pendingAnchor = null
        if (anchor.isEmpty()) return
        val js = "(function(){var e=document.getElementById(${org.json.JSONObject.quote(anchor)});" +
            "if(e){e.scrollIntoView({block:'start'});}})()"
        view.evaluateJavascript(js, null)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        val anchor = intent.getStringExtra(EXTRA_ANCHOR)
        if (!anchor.isNullOrEmpty()) {
            pendingAnchor = anchor
            if (::web.isInitialized) scrollToPendingAnchor(web)
        }
    }

    private fun load(url: String) {        if (!hasNetwork()) {
            showError("当前没有可用网络")
            return
        }
        errorPanel.visibility = View.GONE
        swipe.isRefreshing = true
        web.loadUrl(url)
    }

    private fun showError(reason: String) {
        errorText.text = buildString {
            append("日报加载失败\n\n")
            if (reason.isNotEmpty()) append(reason).append("\n\n")
            append("请检查网络，或点下面的「重试」。\n如果页面更新过，可能只是临时波动。")
        }
        errorPanel.visibility = View.VISIBLE
    }

    private fun hasNetwork(): Boolean {
        val cm = getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val caps = cm.getNetworkCapabilities(cm.activeNetwork) ?: return false
        return caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }

    /**
     * 设置按钮：正常点按只给常用项；按住 6 秒才解锁「在浏览器中打开」「复制日报链接」。
     * 这两项是给自己调试用的，分享给别人时默认看不到。
     */
    private fun handleSettingsTouch(v: View, ev: MotionEvent): Boolean {
        when (ev.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                holdUnlocked = false
                holdStartAt = SystemClock.elapsedRealtime()
                holdHandler.removeCallbacks(unlockTask)
                holdHandler.postDelayed(unlockTask, HOLD_UNLOCK_MS)
                return true
            }
            MotionEvent.ACTION_UP -> {
                holdHandler.removeCallbacks(unlockTask)
                val held = SystemClock.elapsedRealtime() - holdStartAt
                val advanced = holdUnlocked || held >= HOLD_UNLOCK_MS
                holdStartAt = 0L
                v.performClick()
                showMenu(v, advanced)
                return true
            }
            MotionEvent.ACTION_CANCEL -> {
                holdHandler.removeCallbacks(unlockTask)
                holdUnlocked = false
                holdStartAt = 0L
                return true
            }
        }
        return false
    }

    /** 从设置按钮位置向下弹出的下拉菜单，不再用居中的对话框挡住正文。 */
    private fun showMenu(anchor: View, advanced: Boolean = false) {
        val menu = androidx.appcompat.widget.PopupMenu(this, anchor, Gravity.END)
        val group = menu.menu
        val items = mutableListOf("重新加载", "强制刷新（清缓存）", "回到顶部", "调整字号", "检查更新")
        if (advanced) {
            items.add("在浏览器中打开")
            items.add("复制日报链接")
        }
        items.forEachIndexed { i, label -> group.add(0, i, i, label) }
        menu.setOnMenuItemClickListener { item ->
            val label = item.title.toString()
            when (label) {
                "重新加载" -> {
                    web.clearCache(false)
                    load(digestUrl())
                }
                "强制刷新（清缓存）" -> {
                    web.clearCache(true)
                    load(digestUrl())
                }
                "回到顶部" -> {
                    web.scrollTo(0, 0)
                    toast("已回到顶部")
                }
                "调整字号" -> pickTextZoom()
                "检查更新" -> UpdateChecker.check(this, manual = true)
                "在浏览器中打开" -> runCatching {
                    startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(digestUrl())))
                }
                "复制日报链接" -> {
                    val cm = getSystemService(Context.CLIPBOARD_SERVICE) as android.content.ClipboardManager
                    cm.setPrimaryClip(android.content.ClipData.newPlainText("KIKINEWS", digestUrl()))
                    toast("链接已复制")
                }
            }
            true
        }
        menu.gravity = Gravity.END
        menu.show()
    }

    /** 网页缩放比例，手机上按需调大调小，设置会被记住。 */
    private fun pickTextZoom() {
        val steps = arrayOf("小 (85%)", "标准 (100%)", "大 (115%)", "特大 (130%)")
        val values = intArrayOf(85, 100, 115, 130)
        val current = prefs.getInt(KEY_ZOOM, 100)
        val checked = values.indexOf(current).coerceAtLeast(1)
        AlertDialog.Builder(this)
            .setTitle("调整字号")
            .setSingleChoiceItems(steps, checked) { dialog, which ->
                val zoom = values[which]
                web.settings.textZoom = zoom
                prefs.edit().putInt(KEY_ZOOM, zoom).apply()
                dialog.dismiss()
            }
            .setNegativeButton("取消", null)
            .show()
    }

    private fun toast(msg: String) = Toast.makeText(this, msg, Toast.LENGTH_SHORT).show()

    override fun onDestroy() {
        holdHandler.removeCallbacksAndMessages(null)
        super.onDestroy()
    }

    @Suppress("DEPRECATION")
    override fun onBackPressed() {
        if (::web.isInitialized && web.canGoBack()) {
            web.goBack()
        } else {
            super.onBackPressed()
        }
    }
}
