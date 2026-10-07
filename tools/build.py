#!/usr/bin/env python3
"""組裝腳本：讀專案檔，輸出一個可直接開啟的頁面（index.html + style.css + script.js + assets/）。

用法：
    python tools/build.py <專案檔.yaml> [--out 輸出資料夾]

專案檔格式（Phase 1）：
    project: api-ai-hair-extension     # 專案名稱（kebab-case）
    brand: yco                         # 必填：yco｜pfcom，沒有預設值
    title: "頁面標題"                   # 選填，預設用 project
    blocks:
      - block: topbanner               # 區塊內容，欄位見 core/blocks/<區塊>/block.schema.json
        variant: before-after
        ...

區塊也可以是「複數選擇」（評審版，頁面出現切換鈕）：
      - block: topbanner
        mode: multiple                 # single｜multiple；single 要用 use 指定採用哪個候選
        options:                       # 候選代號 a、b、c（至少 2 個、最多 3 個）
          a: {label: 影片版, variant: standard, ...}
          b: {label: 拖曳比較版, variant: before-after, ...}
素材路徑相對於專案檔所在的資料夾。
需要：Python 3.9+、PyYAML、jsonschema。
"""
import argparse
import importlib.util
import json
import re
import shutil
import sys
from html import escape
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parent.parent
MARKER = ".prototype-system-build"
KNOWN_BRANDS = ["yco", "pfcom"]


class BuildError(Exception):
    """可預期的錯誤：直接把訊息顯示給使用者，不需要 traceback。"""


# ---------------------------------------------------------------- 讀檔與驗證
def load_yaml(path):
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise BuildError(f"找不到檔案：{path}")
    except yaml.YAMLError as e:
        raise BuildError(f"專案檔不是正確的 YAML 格式：\n{e}")


def check_project_header(project):
    if not isinstance(project, dict):
        raise BuildError("專案檔內容必須是一組「欄位: 值」的設定。")
    if not project.get("project"):
        raise BuildError("專案檔缺少 project（專案名稱）。")
    brand = project.get("brand")
    if not brand:
        raise BuildError(
            "專案檔沒有指定 brand（品牌）。執行前必須先確定這次做的是 yco 還是 pfcom，沒有預設值。\n"
            "請在專案檔最前面加上一行，例如：brand: yco"
        )
    if brand not in KNOWN_BRANDS:
        raise BuildError(f"不認得的品牌「{brand}」。可用的品牌：{', '.join(KNOWN_BRANDS)}。")
    if brand == "pfcom":
        if project.get("segment") not in ("2c", "2b"):
            raise BuildError("brand 為 pfcom 時，必須另外指定 segment：2c 或 2b。")
    brand_dir = REPO / "brands" / brand
    if not (brand_dir / "brand.yaml").exists():
        raise BuildError(
            f"品牌「{brand}」尚未建立（找不到 brands/{brand}/brand.yaml）。"
            "目前先以 YCO 為主，PF.com 要等 YCO 確定後再建立。"
        )
    if not isinstance(project.get("blocks"), list) or not project["blocks"]:
        raise BuildError("專案檔缺少 blocks（至少要有一個區塊）。")
    return brand_dir


def format_errors(errors, content):
    """把 jsonschema 的錯誤整理成容易讀的中文清單。

    區塊內容有多種格式（variant）時，規格用 oneOf 表示；只顯示符合所選格式的那一支的錯誤，
    並把「因為那一支驗證失敗而連帶產生」的雜訊去掉。
    """
    errors = list(errors)
    variant = content.get("variant")
    branch_props = None
    lines = []
    handled_variant = False
    for e in errors:
        if e.validator != "oneOf":
            continue
        idx = None
        for i, branch in enumerate(e.schema["oneOf"]):
            if branch.get("properties", {}).get("variant", {}).get("const") == variant:
                idx = i
        if idx is None:
            options = [
                b["properties"]["variant"]["const"]
                for b in e.schema["oneOf"]
                if "const" in b.get("properties", {}).get("variant", {})
            ]
            lines.append(f"variant（格式）不是可用的值，可用：{'、'.join(options)}。目前是：{variant!r}")
            handled_variant = True
            continue
        branch_props = set(e.schema["oneOf"][idx].get("properties", {}))
        for sub in e.context:
            if list(sub.schema_path)[0] == idx:
                lines.append(_one(sub))
    for e in errors:
        if e.validator == "oneOf":
            continue
        path = list(e.absolute_path)
        if handled_variant and path == ["variant"]:
            continue
        if e.validator == "unevaluatedProperties":
            if handled_variant:
                continue  # 格式本身就不對，先請使用者改格式，其他欄位的提示只會是雜訊
            names = re.findall(r"'([^']+)'", e.message)
            for name in names:
                if branch_props is not None and name in branch_props:
                    continue  # 該格式本來就有這個欄位，是格式驗證失敗連帶產生的雜訊
                lines.append(f"「{name}」不屬於「{variant}」格式，請移除，或改選其他格式。")
            continue
        lines.append(_one(e))
    seen, out = set(), []
    for line in lines:
        if line not in seen:
            seen.add(line)
            out.append(line)
    return out


def _one(e):
    where = ".".join(str(p) for p in e.absolute_path)
    prefix = f"{where}：" if where else ""
    v = e.validator
    if v == "required":
        name = re.findall(r"'([^']+)'", e.message)
        msg = f"缺少必填欄位「{name[0] if name else '?'}」"
    elif v == "enum":
        msg = f"{e.instance!r} 不是可用的值，可用：{'、'.join(map(str, e.validator_value))}"
    elif v == "const":
        msg = f"必須是 {e.validator_value!r}"
    elif v == "minLength":
        msg = "不能是空白"
    elif v == "minItems":
        msg = f"至少需要 {e.validator_value} 組"
    elif v == "maxItems":
        msg = f"最多 {e.validator_value} 組"
    elif v == "type":
        msg = f"資料型態不對，應為 {e.validator_value}"
    elif v == "additionalProperties":
        names = re.findall(r"'([^']+)'", e.message)
        msg = f"不認得的欄位：{'、'.join(names)}"
    else:
        msg = e.message
    return f"{prefix}{msg}"


# ---------------------------------------------------------------- 區塊與素材
class Context:
    """提供給區塊 render 使用：登記素材並回傳頁面上的網址。"""

    def __init__(self, project_dir, brand_dir, brand_assets):
        self.project_dir = project_dir
        self.brand_dir = brand_dir
        self.brand_assets_declared = set(brand_assets)
        self.project_assets = []   # 相對專案資料夾的路徑
        self.brand_assets_used = []

    def asset(self, rel):
        if rel not in self.project_assets:
            self.project_assets.append(rel)
        return rel

    def brand_asset(self, name):
        if name not in self.brand_assets_declared:
            raise BuildError(f"區塊使用了品牌素材「{name}」，但 brands/*/brand.yaml 的 assets 沒有列出它。")
        if name not in self.brand_assets_used:
            self.brand_assets_used.append(name)
        return f"assets/brand/{name}"


def load_block_module(block_id):
    path = REPO / "core" / "blocks" / block_id / "render.py"
    if not path.exists():
        raise BuildError(f"找不到區塊「{block_id}」（缺少 core/blocks/{block_id}/render.py）。")
    spec = importlib.util.spec_from_file_location(f"block_{block_id}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_option_group():
    path = REPO / "core" / "option-group" / "render.py"
    spec = importlib.util.spec_from_file_location("option_group", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


WRAPPER_KEYS = {"block", "mode", "use", "options"}


def expand_entry(content, label, problems, og):
    """把專案檔裡的一筆區塊設定整理成 (模式, [(候選代號, 候選標籤, 區塊內容), ...])。

    沒有 mode／options 的區塊：就是單一選擇，代號為 None。
    mode: single   → 只取 use 指定的那個候選，不出現切換鈕。
    mode: multiple → 取全部候選（a、b、c，最多 3 個、至少 2 個），出現切換鈕。
    候選的內容格式與一般區塊相同（block 欄位由外層帶入），另可有 label（中文名稱，給人辨認）。
    回傳 None 表示有問題（已記在 problems）。
    """
    if not isinstance(content, dict) or "block" not in content:
        problems.append(f"{label}：缺少 block 欄位（區塊 ID，例如 topbanner）。")
        return None
    if "mode" not in content and "options" not in content and "use" not in content:
        return ("single", [(None, None, content)])
    block_id = content["block"]
    where = f"{label}（{block_id}）"
    extra = sorted(set(content) - WRAPPER_KEYS)
    if extra:
        problems.append(f"{where}：使用 mode／options 時，內容必須寫在各候選（options 底下）裡，不能直接寫在外層：{'、'.join(extra)}")
        return None
    mode = content.get("mode", "single")
    if mode not in ("single", "multiple"):
        problems.append(f"{where}：mode 必須是 single（單一選擇）或 multiple（複數選擇），目前是 {mode!r}。")
        return None
    options = content.get("options")
    if not isinstance(options, dict) or not options:
        problems.append(f"{where}：缺少 options（候選內容），格式為 a:、b:、c: 各一份。")
        return None
    bad = [k for k in options if k not in og.OPTION_CODES]
    if bad:
        problems.append(f"{where}：候選代號只能用 {'、'.join(og.OPTION_CODES)}，不認得：{'、'.join(map(str, bad))}。")
        return None
    codes = [c for c in og.OPTION_CODES if c in options]
    for c in codes:
        if not isinstance(options[c], dict):
            problems.append(f"{where}：候選 {c} 的內容必須是一組「欄位: 值」。")
            return None

    def opt(c):
        body = {k: v for k, v in options[c].items() if k != "label"}
        body["block"] = block_id
        return (c, options[c].get("label"), body)

    if mode == "single":
        use = content.get("use")
        if use not in options:
            problems.append(f"{where}：單一選擇必須用 use 指定採用哪一個候選（{'、'.join(codes)}），目前是 {use!r}。")
            return None
        return ("single", [opt(use)])
    if "use" in content:
        problems.append(f"{where}：複數選擇會輸出全部候選，不需要 use；若要只採用其中一個，請改成 mode: single。")
        return None
    if len(codes) < 2:
        problems.append(f"{where}：複數選擇至少需要 2 個候選（目前只有 {len(codes)} 個）。只有一個版本請改用單一選擇。")
        return None
    return ("multiple", [opt(c) for c in codes])


def render_one(content, label, ctx, problems, toggle=None):
    """驗證並產生一個區塊內容的 HTML。回傳 (html, css 檔, js 檔)，有問題時回傳 None。"""
    block_id = content["block"]
    schema_path = REPO / "core" / "blocks" / block_id / "block.schema.json"
    if not schema_path.exists():
        problems.append(f"{label}：不認得的區塊「{block_id}」。")
        return None
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(content), key=lambda e: list(e.absolute_path))
    if errors:
        for line in format_errors(errors, content):
            problems.append(f"{label}：{line}")
        return None
    mod = load_block_module(block_id)
    if toggle and not getattr(mod, "SUPPORTS_TOGGLE", False):
        problems.append(f"{label}：區塊「{block_id}」尚不支援複數選擇。")
        return None
    try:
        result = mod.render(content, ctx, toggle=toggle) if toggle else mod.render(content, ctx)
    except Exception as e:  # 區塊自己丟的 BlockError 等
        problems.append(f"{label}：{e}")
        return None
    base = REPO / "core" / "blocks" / block_id
    return result["html"], [base / r for r in result.get("css", [])], [base / r for r in result.get("js", [])]


def render_blocks(project, brand_dir, brand_cfg, project_dir):
    ctx = Context(project_dir, brand_dir, brand_cfg.get("assets", []))
    og = load_option_group()
    html_parts, css_files, js_files = [], [], []
    problems = []
    multiple_count = 0

    def add_files(css, js):
        for p in css:
            if p not in css_files:
                css_files.append(p)
        for p in js:
            if p not in js_files:
                js_files.append(p)

    for i, content in enumerate(project["blocks"], start=1):
        label = f"第 {i} 個區塊"
        expanded = expand_entry(content, label, problems, og)
        if expanded is None:
            continue
        mode, options = expanded
        block_id = content["block"]
        if mode == "single":
            code, opt_label, body = options[0]
            suffix = f"（{block_id}" + (f"，候選 {code}" if code else "") + "）"
            r = render_one(body, label + suffix, ctx, problems)
            if r:
                html_parts.append(r[0])
                add_files(r[1], r[2])
            continue
        # 複數選擇
        codes = [c for c, _, _ in options]
        labels = {c: l for c, l, _ in options if l}
        panes, ok = [], True
        for code, _, body in options:
            r = render_one(body, f"{label}（{block_id}，候選 {code}）", ctx, problems, toggle=og.toggles(codes, labels))
            if r is None:
                ok = False
                continue
            panes.append((code, r[0]))
            add_files(r[1], r[2])
        if ok:
            html_parts.append(og.wrap(panes))
            multiple_count += 1
    if problems:
        raise BuildError("內容有以下問題，請修正後再執行：\n  - " + "\n  - ".join(problems))
    missing = [a for a in ctx.project_assets if not (project_dir / a).is_file()]
    if missing:
        raise BuildError("找不到以下素材檔（路徑相對於專案檔所在資料夾）：\n  - " + "\n  - ".join(missing))
    if multiple_count:
        og_dir = REPO / "core" / "option-group"
        css_files.append(og_dir / "style.css")
        js_files.append(og_dir / "behavior.js")
    return html_parts, css_files, js_files, ctx, multiple_count


# ---------------------------------------------------------------- 輸出
def read_text(p):
    return p.read_text(encoding="utf-8")


def write_output(out, project, brand_dir, brand_cfg, html_parts, css_files, js_files, ctx, multiple_count=0):
    if out.exists():
        if not (out / MARKER).exists() and any(out.iterdir()):
            raise BuildError(
                f"輸出資料夾已經有其他檔案，為避免誤刪不會覆蓋：{out}\n"
                "請換一個資料夾，或確認內容可以覆蓋後手動清空它。"
            )
        shutil.rmtree(out)
    out.mkdir(parents=True)
    (out / MARKER).write_text("由 tools/build.py 產生，可以安全覆蓋。\n", encoding="utf-8")

    # 樣式：品牌 → 區塊（共用 → 格式專屬）
    css_chunks = []
    for rel in brand_cfg.get("css", []):
        css_chunks.append(read_text(brand_dir / rel))
    for p in css_files:
        css_chunks.append(read_text(p))
    (out / "style.css").write_text("\n".join(css_chunks), encoding="utf-8")

    has_js = bool(js_files)
    if has_js:
        (out / "script.js").write_text("\n".join(read_text(p) for p in js_files), encoding="utf-8")

    for rel in ctx.project_assets:
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ctx.project_dir / rel, dest)
    for name in ctx.brand_assets_used:
        dest = out / "assets" / "brand" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(brand_dir / "assets" / name, dest)

    fonts = "\n".join(f'<link href="{escape(u)}" rel="stylesheet">' for u in brand_cfg.get("fonts", []))
    if fonts:
        fonts = '<link rel="preconnect" href="https://fonts.googleapis.com">\n' \
                '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n' + fonts
    title = escape(str(project.get("title") or project["project"]))
    body = "\n\n".join(html_parts)
    if multiple_count:
        body = (f'<div class="review-banner" data-review-banner>評審版：含 {multiple_count} 個比較區塊，'
                f'不是正式版</div>\n\n') + body
    script = '\n<script src="script.js"></script>' if has_js else ""
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
{fonts}
<link rel="stylesheet" href="style.css">
</head>
<body>
{body}
{script}
</body>
</html>
"""
    (out / "index.html").write_text(page, encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(description="依專案檔組裝產品頁 prototype")
    ap.add_argument("project_file", help="專案檔（.yaml）")
    ap.add_argument("--out", help="輸出資料夾（預設：dist/<品牌>/<專案名>）")
    args = ap.parse_args(argv)
    try:
        project_path = Path(args.project_file).resolve()
        project = load_yaml(project_path)
        brand_dir = check_project_header(project)
        brand_cfg = load_yaml(brand_dir / "brand.yaml")
        parts, css_files, js_files, ctx, multiple_count = render_blocks(project, brand_dir, brand_cfg, project_path.parent)
        out = Path(args.out).resolve() if args.out else REPO / "dist" / project["brand"] / str(project["project"])
        write_output(out, project, brand_dir, brand_cfg, parts, css_files, js_files, ctx, multiple_count)
    except BuildError as e:
        print(f"[錯誤] {e}", file=sys.stderr)
        return 1
    print(f"完成：{out / 'index.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
