# Topbanner · standard（一般格式：影片＋圖片）

來源：舊流程 DESIGN-RULES.md §5.11；SECTIONS.md Section 01 格式 1。共用規範見上層 `SPEC.md`。

## 概念

背景是一支**循環播放、靜音**的影片，搭配一張圖片（影片載入前或無法播放時顯示的封面）。影片與圖片固定成對出現，三個尺寸各一組。

Figma guideline 原本允許一般格式只用圖片（jpg/png），目前依實際使用情況簡化為成對；之後若出現只有圖片的需求再擴充。

## 素材（每個尺寸 1 支影片＋1 張圖片，共 6 個檔案）

| 欄位 | 用途 | 命名範例 |
|---|---|---|
| `media.dt / pd / mb .video` | 影片（mp4） | `topbanner-video-dt.mp4` |
| `media.dt / pd / mb .poster` | 圖片（封面） | `topbanner-poster-dt.jpg` |

## HTML 與樣式

- 三個 `<video autoplay loop muted playsinline poster="…">`（Desktop / Tablet / Mobile 各一個），每個只包一個 `<source>`，用 CSS `display` 依斷點切換。
- **不要**在單一 `<video>` 裡用多個 `<source media="…">` 切換斷點：這在 `<picture>` 上是標準做法，但在 `<video>` 上瀏覽器支援不穩定，可能載入錯誤斷點的影片。
- `autoplay loop muted playsinline` 是全站影片的共通屬性組合。

## 素材提醒

- **編碼相容性**：舊專案實測 Desktop 影片是 AV1 編碼、Tablet/Mobile 是 H.264。現代 Chrome / Edge / Firefox 都能播放，但 **Safari 要 17 以上**才支援 AV1。收到新影片時，建議用 `ffprobe` 核對編碼是否與前一輪一致，避免無聲切換成支援度較低的編碼。
- **檔案傳輸**：影片檔透過目前的傳輸工具傳到使用者電腦時，H.264 的 mp4 會損毀。處理方式是先打包成 zip 再傳，請使用者手動解壓縮（詳見舊專案 NOTES.md §14）。

## 尚未在新系統驗證

這個格式在舊專案實作過（原 V1），但新系統尚未用實際影片驗證播放。
