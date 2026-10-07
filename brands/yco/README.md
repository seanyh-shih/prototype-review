# brands/yco

YCO 品牌層。放 YCO 專屬的樣式變數、素材與區塊覆寫。

| 檔案 | 內容 |
|---|---|
| `brand.yaml` | 組裝腳本讀取：要載入哪些樣式、字體連結、品牌共用素材 |
| `tokens.css` | 色彩、字體、圓角、header 高度，以及 `--topbanner-*` 的 Topbanner 數值 |
| `base.css` | reset 與全站預設（字體、文字色、圖片、連結） |
| `components/button.css` | Primary 按鈕 |
| `assets/` | 品牌共用素材：Before/After 拖曳把手圖（Desktop／Tablet／Mobile 三張，內容各不相同） |

目前只搬入 Topbanner 用得到的部分，其他區塊搬進來時再逐步增加。來源是舊流程的 `YCO_product page_DESIGN-RULES.md`（章節 3、5.1、5.10）與現有頁面的 `style.css`。
