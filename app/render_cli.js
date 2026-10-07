// 測試用：讀 JSON 專案資料，印出 JS 版產生的 body（資源路徑原樣輸出）。用法：node render_cli.js project.json
const fs = require('fs');
const R = require('./render.js');
const project = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const ctx = { asset: (p) => p, brandAsset: (n) => 'assets/brand/' + n };
try {
  const parts = R.buildParts(project, ctx);
  process.stdout.write(JSON.stringify({ body: parts.body, cssFiles: parts.cssFiles, jsFiles: parts.jsFiles, multipleCount: parts.multipleCount }));
} catch (e) { process.stdout.write(JSON.stringify({ error: e.message })); process.exit(2); }
