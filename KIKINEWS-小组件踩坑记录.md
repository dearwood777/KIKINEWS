# KIKINEWS 桌面小组件踩坑记录

> 这份文档只记「踩过的坑 + 根因 + 正确做法」，不记流水账。
> 目的：无论是我自己下一轮改，还是别的 AI / 别的开发者接手，先读一遍，
> 不要再用已经失败过的方法试第二次。每一条都对应过真实机型上的失败现象。
> 记录时间：2026-11-18（小组件 v1.5.000 → v1.6.006 全程）

---

## 一、最核心的一条：行数不要自己算

**现象**：手机 4×2 第三行只露半行；平板 4×2 拉大后只显示 3 条、下面空约 2/3。

**已经失败过的两条路**（都试过，都别再用）：

1. **用 `OPTION_APPWIDGET_MIN_HEIGHT` 自己估行数**（v1.5.x–v1.6.000）。
   同一个字段各家 launcher 回传的偏差极大：手机偏大 → 按 3 行排版但高度只够 2 行半，第三行被父容器裁掉；平板偏小 → 只排 3 行，下面大片空白。

2. **把 1–8 行的布局全塞进 `RemoteViews(Map<SizeF, RemoteViews>)` 让系统挑**（v1.6.001）。
   看着是 Android 12 官方推荐做法，但它仍然依赖 launcher 报一个可信尺寸。这台平板的 launcher 报的尺寸明显小于真实高度，于是系统每次都挑到 3 行那一档，问题原样复现。

**正确做法 —— 集合型组件（v1.6.002 起）**：
`RemoteViewsService` + `ListView`。布局写「头部固定一行 + ListView `layout_height=0dp` `weight=1`」，条目由 `RemoteViewsFactory` 提供。行数交给系统：装得下几条排几条，超出部分可滚动。App 完全不参与高度计算，所以「留白」「裁半行」从原理上不可能发生。

**代价**：列表可以上下滑（用户明确喜欢这个，不要去掉）；`RemoteViews` 仍然不支持手势翻页，只有 ListView 自身的滚动。

---

## 二、RemoteViews 的硬限制（不清楚就会写出「加不上组件」）

### 2.1 控件白名单 —— 踩过一次，直接表现为「Couldn't add widget」

**现象**：装完 APK 后桌面显示「无法加载组件 / Couldn't add widget」，不能预览、加不上、内容全空。

**根因**：v1.6.005 为了把边框和底板分层，用纯 `android.view.View` 画了一层。**`View` 不在 RemoteViews 允许的控件名单里**，launcher inflate 时直接抛异常，整张卡片作废。

**RemoteViews 布局只能用这些类**：`FrameLayout`、`LinearLayout`、`RelativeLayout`、`GridLayout`、`ImageView`、`TextView`、`Button`、`ListView`、`GridView`、`ProgressBar`、`StackView`、`ViewFlipper`、`AdapterViewFlipper`、`AnalogClock`、`TextClock`、`Chronometer`。

**做法**：需要一层纯装饰背景时，用 `FrameLayout` 只给 `android:background`，不要用 `View`。

**自查命令**（改完布局必跑）：把布局里出现的标签抽出来和白名单比对，任何多出来的类都视为 bug。

### 2.2 只有点击，没有手势

组件内没有滑动/拖拽 API（ListView 的滚动是系统给的例外）。所以滑动翻页做不了，只能点箭头。

### 2.3 列表项点击必须走 fill-in intent

`setRemoteAdapter` 之后，条目本身点击要 `setOnClickFillInIntent(R.id.w_row, Intent().putExtra(锚点…))`，模板用 `setPendingIntentTemplate(R.id.w_list, pendingIntent)`。

**坑**：模板 PendingIntent 的 flag 决定 extras 能不能合并 ——
- Android 12（S）及以上必须 `FLAG_MUTABLE`，否则 fill-in 的 extras 被丢掉，点了没反应；
- Android 12 以下**不能**加 `FLAG_IMMUTABLE`（同样会阻止合并），正确写法是两者都不加。

### 2.4 列表型组件必须声明服务

`AndroidManifest.xml` 里少了这条，列表永远空白：
```xml
<service android:name=".WidgetService"
         android:permission="android.permission.BIND_REMOTEVIEWS"
         android:exported="false" />
```

---

## 三、布局与视觉上的坑

### 3.1 用「组件宽度」判断手机还是平板 —— 会连带放大别的 bug

v1.6.000 里「宽度 ≥300dp 就算平板」。手机 4×2 的宽度正好过线，于是手机误用平板字号与 30dp 行高，把半行问题放大。
**做法**：用 `resources.configuration.smallestScreenWidthDp >= 600` 判断设备类别，不用组件尺寸。

### 3.2 行高用 `layout_weight` 平分 —— 拉大组件就行距爆炸

旧版六行全 `height=0dp, weight=1`，组件一变高，多出的高度摊到每一行，视觉上就是「间距超级大」。
**做法**：行高写死（手机 22/26dp，平板 26/30dp），行数交给列表去装。

### 3.3 固定行高除不尽剩余高度 —— 半行会压框线、压角花

**现象**：最后一行只露一半，被切的文字压在 1dp 描边上、右侧评分撞进右下角花，看上去「文字出框」。

**根因**：列表内容区一直顶到卡片最下沿，裁剪线正好落在视觉边框上。

**做法**：给 ListView 加内缩，并让裁剪尊重内缩：
`android:clipToPadding="true"`、`paddingBottom`（手机 8–10dp、平板 10–12dp）、`paddingEnd`（手机 10–12dp、平板 12–14dp）。
**不要**试图消灭半行——它是「下面还有、可以滑」的提示，和系统滚动列表一致。

### 3.4 边框和底板混在一个 drawable 里 —— 调透明度连框一起淡掉

旧版 11 档 `bg_widget_a000…a100` 里同时画底板和两条描边，透明度作用在整个 drawable 上，框就跟着模糊。
**做法**：底板只留半透明色块；边框单独做成 `frame_widget.xml`（固定不透明），在布局里用一层 `FrameLayout`（**不是 `View`**）叠在底板之上、四角花边与内容之下。
布局顺序：底板（根背景）→ 外框层 → 四角花边 → 内容。

### 3.5 头部贴边

紧凑版（4×1）头部只有 14dp，内容区从 y=0 起排会压在顶部描边上。内容区必须留 `paddingTop`（手机 4dp / 平板 6dp）和左右内边距（12/6dp、平板 14/6dp）。

---

## 四、状态与交互的坑

### 4.1 透明度用了一个全局键 —— 多张卡片互相覆盖

`bg_alpha` 单键存储，4×2 调 20%、4×1 调 80% 时两张都变成 80%。
**做法**：按组件存 `alpha_<组件id>`，`onDeleted` 时连同 `page_<id>`、`seen_<id>` 一起 `remove`。

### 4.2 点齿轮没反应 —— 后台启动 Activity 被拦

旧版「广播 → `context.startActivity`」。Android 10 起从后台启动 Activity 被系统拦截，部分机型点了没反应。
**做法**：直接用 `PendingIntent.getActivity` 指向 `WidgetConfigActivity`，不要绕广播。

### 4.3 多个组件共用 requestCode —— 点 A 的箭头动了 B

所有组件的 PendingIntent 都用固定 requestCode，配上 `FLAG_UPDATE_CURRENT`，后建的会覆盖先建的。
**做法**：`requestCode = (组件id*16 + 槽位)`，并给每个 Intent 加独立 data URI（`kiki://widget/<id>/arrow/<slot>`）。Intent 的 data 参与「是否同一个 PendingIntent」的判定，这是第二重保险。

### 4.4 页号语义 —— 存「首条下标」而不是「第几页」

prs 里 `page_<id>` 存的是当前首条在 items 里的下标，条目按 `(start + i) % total` 循环取。这样最后一屏也永远是满的，不会出现「最后一页只显示两条、下面空着」。
翻页步长 = `baseSlots`，`‹ ›` 跳一屏，跳完调 `notifyAppWidgetViewDataChanged` 让列表重取数据。

---

## 五、picker 标签（显示几乘几）—— 不可控，别硬调

vivo 系 launcher **不认** `targetCellWidth` / `targetCellHeight`（这是 Android 12+ 原生 launcher 的字段），它仍按 `minWidth` 除以每格宽度换算。
- 手机每格约 68dp：340 ÷ 68 ≈ 5 → 显示 5×1 / 5×2
- 平板每格更宽（约 85dp）：340 ÷ 85 = 4 → 显示 4×1 / 4×2

**不要再做的事**：把 `minWidth` 改小去凑手机的 4 列（会让平板反过来算成 3 列）。用户本人已表示「显示啥倒影响不大了」，维持 340dp，标签不一致属于 launcher 侧行为，不影响组件实际渲染。

---

## 六、工程与环境（本机）

- **编译**：`JAVA_HOME=D:\dev\jdk17`、`ANDROID_HOME=D:\dev\android-sdk`、`GRADLE_USER_HOME=D:\dev\gradle-home`，在 `repo/android` 跑 `D:\dev\gradle-8.7\bin\gradle.bat assembleRelease --offline`，约 3–13 分钟。
- **`mergeDexRelease` 报「另一个进程正在使用此文件」**：Gradle 守护进程或杀毒占着文件。先 `gradle --stop`、等几秒、删掉 `app\build\intermediates\dex\release\mergeDexRelease`，再编。
- **`git push` 常报 `Recv failure`**：本机直连 GitHub 不稳，用带重试的脚本（本机 `push2.py`），一般第 2–5 次成功，不要以为一次失败就放弃。
- **本机没有 Android 模拟器、也没有插着设备**（`adb devices` 为空）。所以**任何真机渲染效果都无法在本机验证**：
  能做到的静态核查是 `aapt2 dump badging`（版本号）、`aapt2 dump xmltree --file AndroidManifest.xml`（service/receiver 是否在）、`aapt2 dump resources`（布局资源是否都打进了包）。
  经验教训：不要声称「测过了」，只声明「编译通过 + 静态核查通过，渲染需真机确认」。

---

## 七、给接手者的动作清单

改小组件之前：
1. 先读本文件的「一」和「二.1」——这两条是最贵的两次教训。
2. 不要引入新的「算行数」逻辑；行数只由 ListView 决定。
3. 新加的布局标签必须落在白名单里（第 2.1 节）。
4. 需要分层装饰时用 `FrameLayout` / `ImageView`，绝不用 `View`。

改完必须做：
1. `assembleRelease` 通过。
2. `aapt2 dump badging` 核对 versionName/versionCode。
3. `aapt2 dump xmltree --file AndroidManifest.xml` 核对 service + 两个 receiver。
4. 布局标签白名单自查。
5. 在 `CHANGELOG.md` 记一节，在 `KIKINEWS-项目交接说明.docx` 第 8 章同步口径。
6. 交付时明确写「需要真机确认哪几处」，不要让用户自己猜测什么。
