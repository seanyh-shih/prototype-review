# Topbanner · before-after（拖曳比較）

來源：舊流程 DESIGN-RULES.md §5.10。共用的版面、文字、按鈕規範見上層 `SPEC.md`。

## 概念

兩張照片疊在一起，中間有可拖曳的把手，使用者左右移動來比較前後差異。**只能用圖片（jpg/png），不支援影片。**

## 素材（每個尺寸 2 張，共 6 張）

| 欄位 | 用途 | 命名範例 |
|---|---|---|
| `images.before.dt / pd / mb` | Before 照片 | `topbanner-before-dt.jpg` |
| `images.after.dt / pd / mb` | After 照片 | `topbanner-after-dt.jpg` |

品牌共用素材（不是每個專案要填的）：拖曳把手圖，放在 `brands/<brand>/assets/`：

| 檔案 | 內容 |
|---|---|
| `b_a_sliderContainer.png`（Desktop） | 分隔線＋圓形把手（帶「‹ ›」箭頭）＋BEFORE/AFTER 膠囊標籤 |
| `b_a_sliderContainer_pd.png`（Tablet） | 分隔線＋BEFORE/AFTER 膠囊標籤，**沒有圓形把手** |
| `b_a_sliderContainer_mb.png`（Mobile） | 分隔線＋圓形把手，**沒有 BEFORE/AFTER 標籤** |

三個檔案內容不同，不是同一張圖縮放。把手圖用 `height:100%`、寬度自動，不要拆成多個元素手刻座標。

## DOM 與 class 名稱

```
.topbanner                      區塊（data-variant="before-after"）
├─ .topbanner__media            媒體區（id=topbannerMedia）
│  ├─ <picture> … .topbanner__img--before   Before 照片（底層）
│  ├─ <picture> … .topbanner__img--after    After 照片（上層，被裁切）
│  ├─ .topbanner__handle        拖曳把手（內含三張把手圖，依斷點顯示其一）
│  └─ .topbanner__label--before / --after   Mobile 專用文字標籤
├─ .topbanner__content--desktop
└─ .topbanner__content--narrow
```

圖片切斷點用 `<picture><source media>`：≤768px 用 mb、≤1024px 用 pd、其餘用 dt。

### 舊名稱對新名稱

舊頁面的 class 名稱指的是「裁切邏輯」而不是照片內容，`--before` 裝的是 After 照片，很容易搞錯。新系統改成依照片內容命名：

| 裝的照片 | 舊 class | **新 class** |
|---|---|---|
| Before（底層） | `.topbanner__img--after` | `.topbanner__img--before` |
| After（被裁切） | `.topbanner__img--before` | `.topbanner__img--after` |

JS 函式 `initBeforeAfter(…, beforeImg)` 的 `beforeImg`（被裁切的那層，實際裝 After）也改名為 `clipLayer`。畫面行為與舊頁面完全相同。

## 互動

| 斷點 | 模式 |
|---|---|
| Desktop（≥1025px） | **hover 直接跟隨**：滑鼠移進整個 Topbanner 範圍，不需按住，X 座標即時帶動把手；離開後停在最後位置，不回正中間。原因：Desktop 文字疊在媒體右半，會擋住把手的滑鼠事件，所以改感應整個區塊 |
| Tablet / Mobile | **按住把手拖曳**（mousedown / touchstart），放開後停在放開位置；點媒體任一處可直接跳轉（click-to-jump） |

核心：算出滑鼠 X 相對媒體寬度的百分比，同步設定把手的 `left` 與上層的 `clip-path: inset(0 0 0 N%)`。

## Mobile 的 BEFORE / AFTER 標籤

只在 Mobile 顯示（Desktop/Tablet 的把手圖已內建文字）：

- 直角矩形（`border-radius:0`），不是圓角膠囊
- 左右完全貼齊區塊邊緣（`left:0` / `right:0`），不留邊界
- 背景 `rgba(0,0,0,.6)`、文字白色 16px、`padding:8px 10px`
- 刻意不設 `font-weight`（預設 400），不要覆寫成 600
- 文字可由 `labels.before` / `labels.after` 修改，預設 BEFORE / AFTER
