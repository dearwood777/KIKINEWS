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

    companion object {
        /** 第一次启动用的默认地址：本仓库的 GitHub Pages。 */
        private const val DEFAULT_URL =
            "https://dearwood777.github.io/KIKINEWS/latest.html"

        private const val PREF = "horizon"
        private const val KEY_URL = "digest_url"
        private const val KEY_ZOOM = "text_zoom"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        prefs = getSharedPreferences(PREF, Context.MODE_PRIVATE)
        web = findViewById(R.id.web)
        swipe = findViewById(R.id.swipe)
        errorPanel = findViewById(R.id.errorPanel)
        errorText = findViewById(R.id.errorText)

        setupWebView()

        swipe.setOnRefreshListener { load(digestUrl()) }
        findViewById<View>(R.id.retryButton).setOnClickListener {
            errorPanel.visibility = View.GONE
            load(digestUrl())
        }
        findViewById<View>(R.id.settingsButton).setOnClickListener { showMenu() }

        load(digestUrl())
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

    private fun load(url: String) {
        if (!hasNetwork()) {
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

    private fun showMenu() {
        val items = arrayOf("重新加载", "强制刷新（清缓存）", "回到顶部", "调整字号", "在浏览器中打开", "复制日报链接")
        AlertDialog.Builder(this)
            .setTitle("KIKINEWS 日报")
            .setItems(items) { _, which ->
                when (which) {
                    0 -> {
                        web.clearCache(false)
                        load(digestUrl())
                    }
                    1 -> {
                        web.clearCache(true)
                        load(digestUrl())
                    }
                    2 -> {
                        web.scrollTo(0, 0)
                        toast("已回到顶部")
                    }
                    3 -> pickTextZoom()
                    4 -> runCatching {
                        startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(digestUrl())))
                    }
                    5 -> {
                        val cm = getSystemService(Context.CLIPBOARD_SERVICE) as android.content.ClipboardManager
                        cm.setPrimaryClip(android.content.ClipData.newPlainText("KIKINEWS", digestUrl()))
                        toast("链接已复制")
                    }
                }
            }
            .show()
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

    @Suppress("DEPRECATION")
    override fun onBackPressed() {
        if (::web.isInitialized && web.canGoBack()) {
            web.goBack()
        } else {
            super.onBackPressed()
        }
    }
}
