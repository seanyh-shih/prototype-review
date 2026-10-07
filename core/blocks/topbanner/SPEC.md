# Topbanner 共用規範（三種格式都適用）

來源：舊流程 `YCO_product page_DESIGN-RULES.md` §5.10、§5.11、§5.1，以及 `SECTIONS.md` Section 01。
這份寫的是 **YCO** 的數值；數值本身放在 `brands/yco/tokens.css` 的 `--topbanner-*` 變數。
各格式專屬的規範見 `variants/<variant>/spec.md`。

## 三個斷點

| 名稱 | 範圍 | 版面 |
|---|---|---|
| Desktop（dt） | ≥ 1025px | 媒體滿版；文字疊在右半（寬度 50%）、垂直水平置中、背景透明；區塊高度 = 100vh − header 高度，最小 560px |
| Tablet（pd） | 769–1024px | 圖上文下；媒體比例 1640:970（≈1.69:1） |
| Mobile（mb） | ≤ 768px | 圖上文下；媒體比例 828:584（≈1.42:1） |

- Tablet 與 Mobile 共用同一個「圖下文字區塊」。Figma 只有 dt / mb 兩種 Frame，沒有獨立 Tablet Frame。
- 整個區塊底色 `--topbanner-bg`（`#EDF8F9`），三個斷點共用，不是白色。
- **Desktop 高度依賴 header**：`calc(100vh - var(--header-height))`，預設 64px。做 header 區塊時，高度必須與 `--header-height` 一致。

## 文字

| 斷點 | 標題 h1 | 內文 p |
|---|---|---|
| Desktop、Tablet | 40px／48px，字重 600，字距 −0.5px | 20px／30px，顏色 `--text-strong` |
| Mobile | 32px／40px | 18px／26px |

- Desktop 與 Tablet **共用**同一套字級，只有 Mobile 縮小（跟 Zig-zag「Tablet 另有一套」的規則不同，不要套錯）。
- h1 沒有另外指定顏色，繼承全站文字色；p 明確使用 `--text-strong`。
- 文字區塊寬度上限：基準 440px；Desktop 放寬到 480px；Tablet 放寬到 600px（皆置中於各自容器）。
- 標題字級不為了避免折行而縮小；寬度不夠就自然折行。

## CTA 按鈕

- 最多 2 個，第一個為主要按鈕；兩個都用 Primary（實心藍），不是一實心一外框。
- Desktop / Tablet：高 56px、字級 20px／行高 28px、左右內距 24px；兩顆按鈕 `flex:1` 平分寬度。
- Mobile：維持按鈕預設樣式（高 42px、字級 18px），改直向堆疊、寬度 100%。
- 字重 500（全站按鈕規範）。

## 內容的組成方式

舊頁面的標題、內文、按鈕在 HTML 裡有**兩份重複的區塊**（Desktop 疊字用、Tablet/Mobile 圖下用），用 CSS 的 display 切換，不是同一份內容搬移位置。新系統由組裝腳本用同一份內容資料產生這兩份，填寫內容時**只填一次**。

## 素材尺寸

| 尺寸 | 圖片大小 |
|---|---|
| Desktop | 1920 × 910（約 1920 × 911） |
| Tablet | 1640 × 970 |
| Mobile | 828 × 584 |

三個尺寸各自獨立出圖，不是同一張圖用 CSS 縮放。

## 提醒（每個專案都要核對）

- CTA 文案：Desktop / Tablet / Mobile 應該完全一致。舊專案曾出現 Mobile 與 Desktop 文案不同，經確認是設計稿疏忽。之後遇到不一致時，優先懷疑設計稿、與設計端確認，不要假設是刻意設計，也不要假設一定一致而跳過核對。
- 素材原始檔名沿用設計端提供的檔名（含 `topbannr` 之類的拼字缺漏，不必糾正）；新系統上傳時由系統改成標準名稱（見 `docs/NAMING.md`）。

## 待確認

- **Mobile 內文是否截斷**：舊文件記載 Mobile 內文「最多顯示 3 行」，但舊 CSS 的 `-webkit-line-clamp:3` 缺少 `display:-webkit-box` 等搭配設定，實際沒有生效，內文完整顯示。目前新系統維持完整顯示。是否要真的截斷，請與設計確認。
