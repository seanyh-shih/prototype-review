# topbanner（頁首主視覺）

頁面最上方的主視覺區塊。欄位規格見 [block.schema.json](block.schema.json)。

## 三種格式（variant）

依 Figma guideline，三種格式**互斥**：同一個 Topbanner 只會是其中一種。

| variant | 中文 | 說明 | 範例內容 | 狀態 |
|---|---|---|---|---|
| `standard` | 一般格式 | 背景是一支循環播放的影片，搭配一張圖片（封面），成對出現 | [example.standard-video.yaml](example.standard-video.yaml) | 影片版曾在 API_AI_Hair_Extension 實作過（原 V1）；素材尚未搬入新系統 |
| `before-after` | 拖曳比較 | 兩張圖片，中間可拖曳。只能用圖片 | [example.yaml](example.yaml) | 已實作並驗證，現行 YCO 頁面使用中 |
| `slider` | 圖片輪播 | 多組圖片自動輪播，只有 prompt 提示框文字會隨輪播改變 | [example.slider.yaml](example.slider.yaml) | 規格有，欄位為草稿，**尚未實測** |

`example.yaml` 因為建立時只有 before-after 一種，保留原檔名，內容是 before-after 的範例。

## 各格式要上傳的素材

每種格式都要分 Desktop（dt）／Tablet（pd）／Mobile（mb）三個尺寸。

| 表單下拉選項 | 每個尺寸要上傳 | 合計 | 文字輸入 |
|---|---|---|---|
| 一般格式 | 1 支影片＋1 張圖片（封面） | 6 個檔案 | 無額外 |
| Before/After | Before 圖＋After 圖 | 6 個檔案 | Mobile 標籤文字（選填，進階） |
| Slider | 每組 1 張圖，預設 3 組，可用「＋」增加（不設上限） | 3 組 × 3 尺寸 = 9 個檔案起 | 每組 1 個 prompt 輸入框 |

標題、內文、按鈕是三種格式共用的欄位，換格式時不會變動。

## 表單頁選擇方式（規劃）

1. 格式下拉選單三項：**一般格式、Before/After、Slider**。
2. 「一般格式」固定為影片加圖片成對上傳，沒有「只放圖片」的選項（Figma guideline 原本允許，依實際使用情況簡化；之後若出現只有圖片的需求再擴充）。
3. 上傳區排成表格，橫軸是裝置（Desktop／Tablet／Mobile），直軸是素材，一眼能看出缺哪一格。
4. 在同一個版本裡換格式時，先前上傳的檔案保留、不輸出，換回去不用重傳。

## 內部評估用的 A/B Toggle 不在這裡

之前在頁面上做過的 A/B Toggle，是「內部比較兩個版本」用的選項（option），不屬於 Topbanner 的格式。新系統的做法是「單一選擇／複數選擇」，見 [docs/ARCHITECTURE.md](../../../docs/ARCHITECTURE.md)。舊做法記錄在舊文件 DESIGN-RULES §5.11。
