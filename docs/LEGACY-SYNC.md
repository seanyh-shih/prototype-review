# 新舊流程並行規則

新系統建置期間，舊的 prototype 產出流程暫時保留，因為目前仍有實際需求。

## 舊流程（凍結，不改結構）

- 規範文件：`D:\Website\Claude\system\*.md`
- 輸出位置：`D:\Website\Claude\outputs\<品牌>\<頁面類型>\<專案名>\`
- 不重新命名、不搬動、不調整結構。

## 三條規則

1. **舊流程原地不動。** 新系統的實驗只在這個 repo 裡做。
2. **規則變動只寫一個地方。** 並行期間新發現的樣式規範仍寫進舊的 `system/*.md`。開始搬 Topbanner 時，再從那裡「種」進新系統。
3. **試做範圍只限 Topbanner。** 避免同一件事維護兩份。

## 同步紀錄

| 日期 | 內容 |
|---|---|
| 2026-10-07 | repo 建立，尚未從舊規範文件搬入任何規則 |
| 2026-10-07 | 搬入 Topbanner：DESIGN-RULES §5.10（Before/After）、§5.11（一般格式／影片）、§5.1（Primary 按鈕）、§3 中 Topbanner 用到的色彩，以及 SECTIONS Section 01（三種格式）。YCO 的數值放在 `brands/yco/tokens.css`。與現有 YCO 頁面在 Desktop／Tablet／Mobile 三個寬度比對：計算樣式完全相同、拖曳互動相同，截圖差異僅在子像素等級。**新舊差異**：①Before/After 的 class 改為依照片內容命名（舊頁面 `--before` 裝的是 After 照片）；②Mobile 內文「最多 3 行」舊 CSS 沒有生效，新系統維持完整顯示，待與設計確認 |

之後每次把舊文件的規則搬進新系統，在這裡加一列，寫明日期與搬了哪些區塊。
