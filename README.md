# prototype-system

Prototype builder for PF.com and YCO: block library, content data, assembler.

用「區塊庫 + 內容資料檔 + 組裝腳本」產出產品頁 prototype。長期目標是做成多人共用的表單頁（填欄位、上傳圖片、按鈕產出），所以所有區塊的內容欄位都以規格檔（schema）定義。

## 目前狀態

第一階段（Phase 1）：只做 Topbanner 一個區塊當試做，不做操作介面。Topbanner 的規範與樣式已從舊流程搬入（YCO），並有最小版組裝腳本，可用 Before/After 與一般格式組出頁面；Slider 只有規範。

舊的 prototype 產出流程（`D:\Website\Claude\system\` 與 `outputs\`）暫時保留並行，規則見 [docs/LEGACY-SYNC.md](docs/LEGACY-SYNC.md)。

## 資料夾結構

```
prototype-system/
├─ core/                 共用層：兩個品牌都原樣使用的區塊與規則
│  └─ blocks/
│     └─ topbanner/      區塊：欄位規格、共用樣式、HTML 產生器、各格式（variants/）的規範與樣式
├─ brands/               品牌層：各品牌專屬的樣式變數、素材
│  ├─ yco/               YCO（brand.yaml、tokens.css、base.css、components/、assets/）
│  └─ pfcom/             PF.com（2C 為底，2B 繼承 2C；YCO 確定後再建立）
├─ tools/
│  ├─ build.py           組裝腳本
│  └─ requirements.txt   需要的 Python 套件
├─ docs/                 命名規則、架構說明、新舊流程並行規則
└─ README.md
```

之後會再加入：`projects/`（每個專案的內容資料檔與素材）、`app/`（表單頁）。

## 組裝一個頁面

需要 Python 3.9 以上，並安裝套件：`pip install -r tools/requirements.txt`

```
python tools/build.py <專案檔.yaml> [--out 輸出資料夾]
```

專案檔最前面必須指定 `brand`（`yco` 或 `pfcom`），沒有預設值；格式見 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)。素材路徑相對於專案檔所在的資料夾。不指定 `--out` 時輸出到 `dist/<品牌>/<專案名>/`。內容有問題時，腳本會用中文列出哪裡要修正。

目前尚未支援：複數選擇（`mode`／`options`，Phase 1b）、Slider 格式、YCO 以外的品牌。

## 文件

- [docs/NAMING.md](docs/NAMING.md)：名詞定義與命名規則（先看這份）
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)：分層設計與各階段計畫
- [docs/LEGACY-SYNC.md](docs/LEGACY-SYNC.md)：新舊流程並行期間的規則
