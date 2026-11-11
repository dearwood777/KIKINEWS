# Horizon 日报 → 手机 APK

一句话：**抓取和 AI 全在 GitHub Actions 上跑，产出静态网页；APK 只做一件事——把这个网页显示好。**

```
GitHub Actions（每天 06:00 北京时间，跑在境外服务器）
  ├─ Horizon 抓取 HN / Reddit / RSS / GitHub
  ├─ AI（Gemini 或 Groq）打分、去重、写中英摘要、补背景与讨论
  ├─ scripts/build_latest.py 把最新一期转成手机友好单页
  └─ 发布到 GitHub Pages（gh-pages 分支）
        │
        └─ https://<你>.github.io/<仓库>/latest.html
                 │
                 └─ Android APK（WebView 内核，只负责加载这个地址）
```

APK 里**没有任何 API 密钥**，密钥只存在仓库 Secrets 里。App 只是个"专用浏览器"，所以它永远不会因为模型换血、抓取改版而失效。

## 目录结构

```
horizon-brief/
├─ .github/workflows/horizon-daily.yml   定时流水线
├─ configs/config.actions.gemini.json     Gemini 版配置
├─ configs/config.actions.groq.json       Groq 版配置
├─ scripts/build_latest.py                日报 → 手机单页 HTML
├─ docs/latest.html                       渲染效果预览（可以直接双击看）
└─ android/                               Android Studio 工程
   ├─ app/src/main/java/com/kiki/horizonbrief/MainActivity.kt
   └─ app/src/main/res/...                布局、主题、图标
```

## 部署六步

### 1. 建仓库并放进 Horizon 源码

在你的 GitHub 上新建一个仓库（建议命名 `horizon`，公开仓库不消耗 Actions 额度），然后把：
- Horizon 官方源码（Thysrael/Horizon 的 `main` 分支）作为仓库内容
- 本目录的 `.github/`、`configs/`、`scripts/` 覆盖进对应位置
- 保留 `data/`、`profiles/`、`docs/` 等原有目录

### 2. 配 Secrets

仓库 Settings → Secrets and variables → Actions → New repository secret：

| 名称 | 值 |
|---|---|
| `GOOGLE_API_KEY` | 你的 Gemini key |
| `GROQ_API_KEY` | 你的 Groq key（要用 Groq 时才需要） |

只配一个也能跑，用哪个就在手动触发时选哪个。

### 3. 打开 Pages

仓库 Settings → Pages → Source 选 **Deploy from a branch** → 分支选 `gh-pages`，目录 `/ (root)`。
第一次跑完 workflow 之后 `gh-pages` 分支才会出现，出现之后再回来设置。

### 4. 先手动跑一次

仓库 Actions 标签 → 左侧 `Horizon Daily Digest` → Run workflow → provider 选 `gemini`。
大约 5–15 分钟，日志里出现 `Saved ZH summary to: data/summaries/...` 就成了。

跑完确认这个地址能打开：

```
https://<你的用户名>.github.io/<仓库名>/latest.html
```

### 5. 编译 APK

用 Android Studio 打开 `android/` 目录（不是外层 horizon-brief）。首次同步会下载 Gradle 8.7 和依赖。

**必须改一处**：`app/src/main/java/com/kiki/horizonbrief/MainActivity.kt` 里的

```kotlin
private const val DEFAULT_URL = "https://your-name.github.io/your-repo/latest.html"
```

改成你第 4 步验证过的真实地址。

然后 Build → Build Bundle(s)/APK(s) → Build APK(s)，输出在
`android/app/build/outputs/apk/debug/app-debug.apk`，装到手机即可。

> 不装 APK 也能用：手机浏览器打开 `latest.html` → 菜单"添加到主屏幕"，得到的效果和 APK 几乎一样，还省了编译。

### 6. 以后每天自动跑

workflow 里的 `cron: "0 22 * * *"` = 北京时间 06:00。想换时间就改这个 cron（GitHub 用 UTC，北京时间减 8 小时）。

## 关于"打包进 APK"的三种做法，我的取舍

| 做法 | 效果 | 问题 |
|---|---|---|
| **A. WebView 在线加载（本方案）** | 每天打开就是最新一期，零维护 | 没网打不开 |
| B. 把某一期 HTML 塞进 APK assets | 完全离线 | 内容永远冻结在编译那天，等于"日报"变成"某一期" |
| C. A + 本地缓存上一期 | 有网看最新，没网看昨天 | 多一点代码，收益明显 |

我现在实现的是 **A**，并在 WebView 层面开了缓存（`LOAD_DEFAULT` + DOM storage），弱网时能回落到缓存页面。如果你要 **C**，我可以在 MainActivity 里加一段"加载成功后把 HTML 存到内部存储、失败时读它"的逻辑，代码量大概 40 行。

另外两种展示上的改进，成本也不高：
- **顶部日期切换器**：读 `latest.json` 和 gh-pages 目录，做往期回看（现在点站点首页也能看往期列表）
- **只留中文**：`configs` 里把 `languages` 改成 `["zh"]`，省一半 token，页面更短

## 已经实测过的两件事，别踩坑

1. **Gemini / Groq 在你本地和这台云主机上都连不通**（Google 超时、Groq TLS 被重置）。所以本地调试只能走 Ollama，云端跑只能靠 GitHub Actions——这不是配置问题，是网络出口问题。
2. **Horizon 的配置是 JSON，不是 YAML**，文件名必须是 `data/config.json`；`api_key_env` 里填的是**环境变量名**，不是密钥本身。

## 已知限制

- 稳妥起见，Actions 版配置关掉了 Telegram 和 Twitter/X（需要额外凭证且容易失败），保留 HN / Reddit / RSS / GitHub。
- Groq 的 `llama-3.1-8b-instant` 质量比 Gemini Flash 弱，适合当省钱备用；主力建议 Gemini。
- GitHub 免费额度：公开仓库 Actions 不限时，私有仓库每月 2000 分钟，本流程单次约 5–15 分钟，够用。

## 编译时的一个小提醒

工程里带了 `gradle/wrapper/gradle-wrapper.properties`，但**没有 `gradle-wrapper.jar`**（二进制没法在这里生成）。
Android Studio 打开后如果提示 wrapper 缺失，按提示让它生成即可；或者在
Settings → Build, Execution, Deployment → Build Tools → Gradle 里选
"Use Gradle from: gradle-wrapper.properties" / 本地 Gradle 8.7。
