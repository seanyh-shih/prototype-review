# prototype-system

Prototype builder for PF.com and YCO: block library, content data, assembler.

用「區塊庫 + 內容資料檔 + 組裝腳本」產出產品頁 prototype。長期目標是做成多人共用的表單頁（填欄位、上傳圖片、按鈕產出），所以所有區塊的內容欄位都以規格檔（schema）定義。

## 目前狀態

第一階段（Phase 1）：只做 Topbanner 一個區塊當試做，不做操作介面。

舊的 prototype 產出流程（`D:\Website\Claude\system\` 與 `outputs\`）暫時保留並行，規則見 [docs/LEGACY-SYNC.md](docs/LEGACY-SYNC.md)。

## 資料夾結構

```
prototype-system/
├─ core/                 共用層：兩個品牌都原樣使用的區塊與規則
│  └─ blocks/
│     └─ topbanner/      區塊：結構、樣式、欄位規格(block.schema.json)、範例內容
├─ brands/               品牌層：各品牌專屬的樣式、素材、區塊覆寫
│  ├─ pfcom/             PF.com（2C 為底，2B 繼承 2C）
│  └─ yco/               YCO
├─ docs/                 命名規則、架構說明、新舊流程並行規則
└─ README.md
```

之後會再加入：`projects/`（每個專案的內容資料檔與素材）、`tools/`（組裝腳本）、`app/`（表單頁）。

## 文件

- [docs/NAMING.md](docs/NAMING.md)：名詞定義與命名規則（先看這份）
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)：分層設計與各階段計畫
- [docs/LEGACY-SYNC.md](docs/LEGACY-SYNC.md)：新舊流程並行期間的規則
