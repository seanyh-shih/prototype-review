# 命名規則

## 名詞定義（避免混用）

過去「A/B」「V1/V2」「_A/_B」「v67 資料夾」混著使用，這裡把它們拆開，各用一個詞。

| 名詞 | 英文 | 意思 | 例子 |
|---|---|---|---|
| 區塊 | block | 頁面上的一個功能區 | `topbanner`、`faq-accordion` |
| 變體 | variant | 同一個區塊的不同「呈現格式」，會出現在正式頁面上 | `topbanner` 的 `before-after`、`video` |
| 選項 | option | 內部用來比較評估的候選版本，評估完會選定或淘汰，不是最終頁面的一部分 | 原本的 A/B Toggle |
| 修訂 | revision | 檔案隨時間的修改紀錄，交給 Git 管，不寫進檔名 | commit 紀錄 |
| 品牌 | brand | 產品線，決定樣式與素材 | `pfcom`、`yco` |
| 專案 | project | 一個產品頁 | `api-ai-hair-extension` |

規則：檔名和欄位名稱裡**不要出現** `v1`、`v2`、`final`、`new`、`copy` 這類版本字樣。版本交給 Git，呈現格式用 variant。

## 區塊命名

- 區塊 ID 用英文小寫加連字號（kebab-case），依「功能」命名，**不依位置編號**。
  - 好：`topbanner`、`zigzag`、`step-list`、`faq-accordion`
  - 不好：`section-01`、`block-3`（頁面順序一變就失效）
- 每個區塊另有一個中文顯示名稱，給表單頁和文件使用。
- 區塊 ID 一旦決定就不再更動；要改顯示名稱可以隨時改。
- CSS 沿用既有的 BEM：`.topbanner`、`.topbanner__media`、`.topbanner--before-after`。

## 欄位命名

- 內容資料檔的欄位用小寫駝峰（lowerCamelCase），例如 `heading`、`ctas`、`images`。
- 裝置縮寫固定三個：`dt`（Desktop）、`pd`（Tablet）、`mb`（Mobile），沿用 Figma 與既有素材的前綴。

## 素材命名

```
{block}-{slot}-{device}.{ext}
```

例：`topbanner-before-dt.jpg`、`topbanner-after-mb.jpg`

## 資料夾命名

- 全部小寫、連字號，不用空格和中文（避免跨系統與網址問題）。
- 專案資料夾使用專案名稱的 kebab-case，例如 `api-ai-hair-extension`。

## 待辦

- 其他區塊（YCO 目前 18 個 Section）的 ID 與中文顯示名稱，等 Topbanner 試做完成後逐一定案，**不在這次一次做完**。
