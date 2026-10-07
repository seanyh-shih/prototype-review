"""測試共用工具：用合成素材組出測試專案、呼叫組裝腳本、開瀏覽器。

素材都是測試時當場產生的小圖與假影片，不依賴任何真實素材。
瀏覽器測試需要 Chromium：預設用 Playwright 內建的；
若在特殊環境（例如沙箱）要指定位置，設環境變數 CHROMIUM_PATH。
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from PIL import Image

REPO = Path(__file__).resolve().parent.parent
BUILD = REPO / "tools" / "build.py"

SIZES = {"dt": (1920, 1080), "pd": (1640, 970), "mb": (828, 584)}
COLORS = {"before": (200, 60, 60), "after": (60, 60, 200), "poster": (60, 160, 60)}

BODY = "Integrate highly realistic, AI-powered virtual try-ons into your platform."
HEAD = "AI Hair Extension Virtual Try-On API"


def _make_assets(root: Path):
    (root / "assets").mkdir(parents=True, exist_ok=True)
    for slot, color in COLORS.items():
        for dev, size in SIZES.items():
            Image.new("RGB", size, color).save(root / "assets" / f"topbanner-{slot}-{dev}.jpg")
    for dev in SIZES:
        (root / "assets" / f"topbanner-video-{dev}.mp4").write_bytes(b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 64)


def common(variant):
    return {
        "block": "topbanner", "variant": variant, "heading": HEAD, "body": BODY,
        "ctas": [{"label": "Contact Us", "href": "#"}, {"label": "API Documentation", "href": "#"}],
    }


def before_after_block():
    b = common("before-after")
    b["images"] = {s: {d: f"assets/topbanner-{s}-{d}.jpg" for d in SIZES} for s in ("before", "after")}
    return b


def standard_block():
    b = common("standard")
    b["media"] = {d: {"video": f"assets/topbanner-video-{d}.mp4", "poster": f"assets/topbanner-poster-{d}.jpg"} for d in SIZES}
    return b


def write_project(root: Path, blocks, **header):
    _make_assets(root)
    data = {"project": "test-project", "brand": "yco", "title": "測試頁", **header, "blocks": blocks}
    p = root / "project.yaml"
    p.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return p


def run_build(project_file: Path, out: Path = None):
    cmd = [sys.executable, str(BUILD), str(project_file)]
    if out:
        cmd += ["--out", str(out)]
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")


@pytest.fixture
def built(tmp_path_factory):
    """回傳 build(blocks) → 輸出資料夾（含 index.html），失敗直接讓測試報錯。"""
    def _build(blocks, name="p"):
        root = tmp_path_factory.mktemp(name)
        proj = write_project(root, blocks)
        out = root / "out"
        r = run_build(proj, out)
        assert r.returncode == 0, r.stderr
        return out
    return _build


@pytest.fixture(scope="session")
def browser():
    pw_mod = pytest.importorskip("playwright.sync_api")
    with pw_mod.sync_playwright() as pw:
        kw = {"args": ["--no-sandbox"]}
        if os.environ.get("CHROMIUM_PATH"):
            kw["executable_path"] = os.environ["CHROMIUM_PATH"]
        b = pw.chromium.launch(**kw)
        yield b
        b.close()


VIEWPORTS = {"desktop": (1440, 900), "tablet": (900, 1100), "mobile": (390, 844)}


@pytest.fixture
def open_page(browser):
    """open_page(out_dir, "desktop") → page。擋掉外部網路（Google Fonts），只讀本機檔案。"""
    pages = []

    def _open(out_dir: Path, device: str):
        w, h = VIEWPORTS[device]
        ctx = browser.new_context(viewport={"width": w, "height": h}, has_touch=(device != "desktop"))
        page = ctx.new_page()
        page.route("**/*", lambda route: route.continue_() if route.request.url.startswith("file:") else route.abort())
        page.goto((out_dir / "index.html").as_uri())
        page.wait_for_load_state("load")
        pages.append(ctx)
        return page
    yield _open
    for c in pages:
        c.close()


def option_block(mode="multiple", use=None, codes=("a", "b"), variants=None):
    """複數／單一選擇的區塊設定。預設 a=一般格式、b=拖曳比較、c=一般格式。"""
    makers = {"a": ("影片版", standard_block), "b": ("拖曳比較版", before_after_block), "c": ("第三版", standard_block)}
    options = {}
    for c in codes:
        label, mk = makers[c]
        body = mk()
        body.pop("block")
        options[c] = {"label": label, **body}
    out = {"block": "topbanner", "mode": mode, "options": options}
    if use:
        out["use"] = use
    return out
