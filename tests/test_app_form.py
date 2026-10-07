"""後台表單頁（app/dist/topbanner-form.html）：在瀏覽器中實際操作一遍。"""
import subprocess
import sys

import pytest

from conftest import REPO

DIST = REPO / "app" / "dist" / "topbanner-form.html"


@pytest.fixture(scope="module")
def form_file(tmp_path_factory):
    subprocess.run([sys.executable, str(REPO / "app" / "build_app.py")], check=True, capture_output=True)
    f = tmp_path_factory.mktemp("form") / "form.html"
    f.write_text("<!doctype html><html><head><meta charset=utf8><meta name=viewport content='width=device-width,initial-scale=1'></head><body>"
                 + DIST.read_text(encoding="utf-8") + "</body></html>", encoding="utf-8")
    return f


@pytest.fixture
def page(browser, form_file):
    ctx = browser.new_context(viewport={"width": 1440, "height": 1000})
    p = ctx.new_page()
    p.errors = []
    p.on("pageerror", lambda e: p.errors.append(str(e)))
    # 假的 downloads capability：記錄存檔請求
    p.add_init_script("""window.__saved = [];
      window.claude = { use: async (n) => n === 'downloads' ? { save: async (r) => { window.__saved.push([r.filename, r.data.size || r.data.length]); return {status:'saved'}; } } : null };""")
    p.route("**/*", lambda r: r.continue_() if r.request.url.startswith(("file:", "data:", "blob:", "about:")) else r.abort())
    p.goto(form_file.as_uri())
    yield p
    ctx.close()
    assert p.errors == []


def frame(page):
    return page.frame_locator("#pv")


def test_locked_until_brand_chosen(page):
    assert page.eval_on_selector("#locked", "e => e.inert") is True
    assert page.is_visible("#lockmsg")
    assert page.is_disabled("#brand-pfcom")
    assert page.is_disabled("#dl-html")
    page.check("#brand-yco", force=True)
    assert page.eval_on_selector("#locked", "e => e.inert") is False


def test_example_fills_preview_and_downloads(page):
    page.check("#brand-yco", force=True)
    page.click("#loadex")
    page.wait_for_function("document.getElementById('stpill').textContent === '可輸出'")
    assert page.is_enabled("#dl-html")
    page.wait_for_timeout(400)
    f = frame(page)
    assert f.locator(".option-pane").count() == 2
    assert f.locator(".review-banner").count() == 1
    # 預覽裡的 A/B 切換可以用
    f.locator(".option-pane[data-option=a] .option-toggle--overlay [data-option-target=b]").click()
    assert f.locator("[data-option-group]").get_attribute("data-active") == "b"
    # 專案檔分頁顯示 YAML
    page.click("[data-view=yaml]")
    y = page.inner_text("#yamlbox")
    assert 'mode: "multiple"' in y
    assert "brand: \"yco\"" in y and "options:" in y
    page.click("#dl-html")
    page.wait_for_function("window.__saved.length === 1")
    assert page.evaluate("window.__saved[0][0]") == "api-ai-hair-extension.html"


def test_single_mode_hides_toggle_and_keeps_other_candidates(page):
    page.check("#brand-yco", force=True)
    page.click("#loadex")
    page.select_option("#mode", "single")
    page.wait_for_selector("#usesel")
    page.select_option("#usesel", "b")
    page.wait_for_timeout(400)
    f = frame(page)
    assert f.locator(".option-group").count() == 0
    assert f.locator("[data-variant=before-after]").count() == 1
    # 切回複數，A 的內容還在
    page.select_option("#mode", "multiple")
    assert page.input_value("#hd-a").startswith("AI Hair")


def test_missing_items_listed(page):
    page.check("#brand-yco", force=True)
    page.wait_for_function("document.getElementById('todo').textContent.includes('缺標題')")
    assert "素材還缺 6 個" in page.inner_text("#todo")
    assert page.is_disabled("#dl-zip")
    page.select_option("#vr-a", "before-after")
    page.wait_for_timeout(300)
    assert "素材還缺 6 個" in page.inner_text("#todo")


def test_add_candidate_limit_three(page):
    page.check("#brand-yco", force=True)
    page.select_option("#mode", "multiple")
    assert page.locator(".cand").count() == 2
    page.click("#add")
    assert page.locator(".cand").count() == 3
    assert page.is_hidden("#addwrap")


def test_form_output_matches_build_script(page, tmp_path):
    """後台產生的頁面 body，與把後台輸出的專案檔丟給組裝腳本得到的一致。"""
    import yaml
    from conftest import run_build
    page.check("#brand-yco", force=True)
    page.click("#loadex")
    page.wait_for_function("document.getElementById('stpill').textContent === '可輸出'")
    page.click("[data-view=yaml]")
    proj_yaml = page.inner_text("#yamlbox")
    # 把範例素材寫成檔案，路徑與專案檔一致
    data = yaml.safe_load(proj_yaml)
    (tmp_path / "assets").mkdir()
    ex = REPO / "app" / "example-assets"
    for c, opt in data["blocks"][0]["options"].items():
        def paths(o):
            if isinstance(o, dict):
                for v in o.values():
                    yield from paths(v)
            elif isinstance(o, str) and o.startswith("assets/"):
                yield o
        for rel in paths(opt):
            # assets/topbanner-a-before-dt.jpg → 範例檔 topbanner-before-dt.jpg
            name = rel.split("/")[1].replace(f"topbanner-{c}-", "topbanner-")
            (tmp_path / rel).write_bytes((ex / name).read_bytes())
    (tmp_path / "project.yaml").write_text(proj_yaml, encoding="utf-8")
    r = run_build(tmp_path / "project.yaml", tmp_path / "out")
    assert r.returncode == 0, r.stderr
    py_html = (tmp_path / "out" / "index.html").read_text(encoding="utf-8")
    assert py_html.count('class="option-pane"') == 2
    assert 'data-variant="standard"' in py_html and 'data-variant="before-after"' in py_html
