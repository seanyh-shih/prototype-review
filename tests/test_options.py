"""複數選擇（單一選擇／複數選擇）：組裝腳本的規則與瀏覽器中的切換行為。"""
import pytest

from conftest import before_after_block, option_block, run_build, standard_block, write_project
from test_topbanner import box, css


def build(tmp_path, blocks):
    proj = write_project(tmp_path, blocks)
    r = run_build(proj, tmp_path / "out")
    return r, tmp_path / "out"


# ------------------------------------------------------------------ 組裝規則
def test_multiple_outputs_all_options_and_banner(tmp_path):
    r, out = build(tmp_path, [option_block()])
    assert r.returncode == 0, r.stderr
    html = (out / "index.html").read_text(encoding="utf-8")
    assert html.count('class="option-pane"') == 2
    assert 'data-active="a"' in html and html.count("data-option-target=\"a\"") == 4  # 每個候選 2 顆（Desktop／Tablet-Mobile）
    assert "評審版：含 1 個比較區塊" in html
    assert " id=" not in html
    assert (out / "script.js").exists()
    assert "option-toggle" in (out / "style.css").read_text(encoding="utf-8")


def test_three_options(tmp_path):
    r, out = build(tmp_path, [option_block(codes=("a", "b", "c"))])
    assert r.returncode == 0, r.stderr
    html = (out / "index.html").read_text(encoding="utf-8")
    assert html.count('class="option-pane"') == 3
    assert 'data-option-target="c"' in html


def test_single_mode_outputs_only_chosen_without_toggle(tmp_path):
    r, out = build(tmp_path, [option_block(mode="single", use="b")])
    assert r.returncode == 0, r.stderr
    html = (out / "index.html").read_text(encoding="utf-8")
    assert "option-group" not in html and "option-toggle" not in html and "review-banner" not in html
    assert 'data-variant="before-after"' in html and "<video" not in html
    assert not (out / "assets" / "topbanner-video-dt.mp4").exists(), "沒被採用的候選，素材不輸出"


def test_single_mode_same_as_plain_block(tmp_path):
    """單一選擇的輸出，要和直接寫一般區塊完全一樣。"""
    (tmp_path / "opt").mkdir()
    (tmp_path / "plain").mkdir()
    _, out1 = build(tmp_path / "opt", [option_block(mode="single", use="b")])
    _, out2 = build(tmp_path / "plain", [before_after_block()])
    assert (out1 / "index.html").read_text(encoding="utf-8") == (out2 / "index.html").read_text(encoding="utf-8")


@pytest.mark.parametrize("block,expect", [
    (lambda: option_block(codes=("a",)), "至少需要 2 個候選"),
    (lambda: option_block(mode="single"), "必須用 use 指定"),
    (lambda: option_block(mode="single", use="c"), "必須用 use 指定"),
    (lambda: option_block(use="a"), "不需要 use"),
    (lambda: {**option_block(), "mode": "both"}, "mode 必須是"),
    (lambda: {**option_block(), "heading": "x"}, "不能直接寫在外層"),
    (lambda: {"block": "topbanner", "mode": "multiple"}, "缺少 options"),
])
def test_invalid_option_configs(tmp_path, block, expect):
    r, _ = build(tmp_path, [block()])
    assert r.returncode == 1
    assert expect in r.stderr, r.stderr


def test_unknown_option_code(tmp_path):
    b = option_block()
    b["options"]["d"] = b["options"]["a"]
    r, _ = build(tmp_path, [b])
    assert r.returncode == 1 and "候選代號只能用" in r.stderr


def test_option_content_errors_name_the_option(tmp_path):
    b = option_block()
    del b["options"]["b"]["heading"]
    r, _ = build(tmp_path, [b])
    assert r.returncode == 1
    assert "候選 b" in r.stderr and "缺少必填欄位「heading」" in r.stderr


# ------------------------------------------------------------------ 瀏覽器行為
@pytest.fixture(scope="module")
def multi_out(tmp_path_factory):
    root = tmp_path_factory.mktemp("multi")
    proj = write_project(root, [option_block(codes=("a", "b", "c"))])
    assert run_build(proj, root / "out").returncode == 0
    return root / "out"


def active(page):
    return page.eval_on_selector("[data-option-group]", "e => e.getAttribute('data-active')")


def visible_panes(page):
    return page.eval_on_selector_all(
        ".option-pane", "els => els.filter(e => getComputedStyle(e).display !== 'none').map(e => e.dataset.option)")


def visible_toggle(page):
    """目前畫面上看得到的切換鈕（每個斷點只應有一組）。"""
    return page.eval_on_selector_all(
        ".option-toggle", """els => els.filter(e => e.getClientRects().length && getComputedStyle(e).display !== 'none'
            && e.closest('.option-pane') && getComputedStyle(e.closest('.option-pane')).display !== 'none').length""")


@pytest.mark.parametrize("device", ["desktop", "tablet", "mobile"])
def test_default_shows_a_and_one_toggle(open_page, multi_out, device):
    page = open_page(multi_out, device)
    assert active(page) == "a" and visible_panes(page) == ["a"]
    assert visible_toggle(page) == 1


@pytest.mark.parametrize("device", ["desktop", "tablet", "mobile"])
def test_click_switches_and_syncs_visual(open_page, multi_out, device):
    page = open_page(multi_out, device)
    kind = "overlay" if device == "desktop" else "inline"
    page.click(f".option-pane[data-option=a] .option-toggle--{kind} [data-option-target=b]")
    assert active(page) == "b" and visible_panes(page) == ["b"]
    assert page.eval_on_selector(".option-pane[data-option=b] .topbanner", "e => e.dataset.variant") == "before-after"
    # 選中樣式：B 深灰實心、A 透明
    sel = f".option-pane[data-option=b] .option-toggle--{kind}"
    assert css(page, f"{sel} [data-option-target=b]", "backgroundColor") == "rgb(147, 147, 147)"
    assert css(page, f"{sel} [data-option-target=a]", "backgroundColor") == "rgba(0, 0, 0, 0)"
    assert page.get_attribute(f"{sel} [data-option-target=b]", "aria-pressed") == "true"
    page.click(f"{sel} [data-option-target=c]")
    assert active(page) == "c" and visible_panes(page) == ["c"]
    page.click(f".option-pane[data-option=c] .option-toggle--{kind} [data-option-target=a]")
    assert active(page) == "a"


def test_toggle_geometry(open_page, multi_out):
    d = open_page(multi_out, "desktop")
    t = box(d, ".option-pane[data-option=a] .option-toggle--overlay")
    s = box(d, ".option-pane[data-option=a] .topbanner")
    assert t["h"] == 44
    assert abs((s["x"] + s["w"]) - (t["x"] + t["w"]) - 77) < 1, "右邊 77px"
    assert abs((s["y"] + s["h"]) - (t["y"] + t["h"]) - 36) < 1, "下方 36px"
    assert css(d, ".option-pane[data-option=a] .option-toggle--overlay", "borderRadius") != "0px"

    for device in ("tablet", "mobile"):
        p = open_page(multi_out, device)
        t = box(p, ".option-pane[data-option=a] .option-toggle--inline")
        h = box(p, ".option-pane[data-option=a] .topbanner__heading-row h1")
        row = box(p, ".option-pane[data-option=a] .topbanner__heading-row")
        assert t["h"] == 34, "Tablet/Mobile 縮小為 34px 高"
        assert t["x"] + t["w"] <= row["x"] + row["w"] + 0.5 and row["x"] + row["w"] - (t["x"] + t["w"]) < 1, "靠右"
        assert abs((t["y"] + t["h"] / 2) - (h["y"] + h["h"] / 2)) < 30, "與標題同一列"
        assert p.evaluate("document.documentElement.scrollWidth") <= p.viewport_size["width"]


def test_inactive_videos_paused_and_active_played(open_page, multi_out):
    """測試用的假影片無法真的播放，所以改為記錄 play()／pause() 被呼叫的情形。"""
    page = open_page(multi_out, "desktop")
    page.evaluate("""() => {
        window.__calls = [];
        for (const m of ['play', 'pause']) {
            const orig = HTMLMediaElement.prototype[m];
            HTMLMediaElement.prototype[m] = function () {
                window.__calls.push([m, this.closest('.option-pane').dataset.option]);
                return m === 'play' ? Promise.resolve() : undefined;
            };
        }
    }""")
    page.click(".option-pane[data-option=a] .option-toggle--overlay [data-option-target=b]")
    calls = page.evaluate("window.__calls")
    assert ["pause", "a"] in calls, "切走後原本的影片要暫停"
    assert ["play", "c"] not in calls and ["play", "a"] not in calls
    page.click(".option-pane[data-option=b] .option-toggle--overlay [data-option-target=c]")
    calls = page.evaluate("window.__calls")
    assert ["play", "c"] in calls, "切到有影片的候選要播放"


def test_before_after_works_inside_option(open_page, multi_out):
    page = open_page(multi_out, "desktop")
    page.click(".option-pane[data-option=a] .option-toggle--overlay [data-option-target=b]")
    m = box(page, ".option-pane[data-option=b] .topbanner__media")
    page.mouse.move(m["x"] + m["w"] * 0.3, m["y"] + 100)
    page.mouse.move(m["x"] + m["w"] * 0.3 + 1, m["y"] + 100)
    v = page.eval_on_selector(".option-pane[data-option=b] .topbanner__img--after", "e => e.style.clipPath")
    assert v.startswith("inset(0px 0px 0px 30"), v
    # 另一個候選（影片版）不受影響
    assert page.eval_on_selector(".option-pane[data-option=a] .topbanner", "e => e.dataset.variant") == "standard"
