"""Topbanner 在真實瀏覽器中的外觀與互動（Desktop / Tablet / Mobile 三種視窗）。"""
import pytest

from conftest import before_after_block, standard_block

DEVICES = ["desktop", "tablet", "mobile"]


@pytest.fixture(scope="module")
def ba_out(tmp_path_factory):
    from conftest import run_build, write_project
    root = tmp_path_factory.mktemp("ba")
    proj = write_project(root, [before_after_block()])
    assert run_build(proj, root / "out").returncode == 0
    return root / "out"


@pytest.fixture(scope="module")
def std_out(tmp_path_factory):
    from conftest import run_build, write_project
    root = tmp_path_factory.mktemp("std")
    proj = write_project(root, [standard_block()])
    assert run_build(proj, root / "out").returncode == 0
    return root / "out"


def css(page, selector, prop):
    return page.eval_on_selector(selector, f"e => getComputedStyle(e).{prop}")


def box(page, selector):
    return page.eval_on_selector(selector, "e => { const r = e.getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height}; }")


def visible_text_block(page):
    """目前可見的那份文字內容區塊的 selector。"""
    for sel in (".topbanner__content--desktop", ".topbanner__content--narrow"):
        if css(page, sel, "display") != "none":
            return sel
    raise AssertionError("沒有任何文字區塊可見")


# ------------------------------------------------------------------ 共用（兩種格式）
@pytest.mark.parametrize("variant,fixture", [("before-after", "ba_out"), ("standard", "std_out")])
@pytest.mark.parametrize("device", DEVICES)
def test_layout_common(request, open_page, variant, fixture, device):
    page = open_page(request.getfixturevalue(fixture), device)
    vw = page.viewport_size["width"]
    assert page.evaluate("document.documentElement.scrollWidth") <= vw, "不能橫向溢出"
    assert css(page, ".topbanner", "backgroundColor") == "rgb(237, 248, 249)"

    sel = visible_text_block(page)
    assert sel == (".topbanner__content--desktop" if device == "desktop" else ".topbanner__content--narrow")
    other = ".topbanner__content--narrow" if device == "desktop" else ".topbanner__content--desktop"
    assert css(page, other, "display") == "none"

    h1_size, h1_line = {"desktop": ("40px", "48px"), "tablet": ("40px", "48px"), "mobile": ("32px", "40px")}[device]
    p_size, p_line = {"desktop": ("20px", "30px"), "tablet": ("20px", "30px"), "mobile": ("18px", "26px")}[device]
    assert css(page, f"{sel} h1", "fontSize") == h1_size
    assert css(page, f"{sel} h1", "lineHeight") == h1_line
    assert css(page, f"{sel} p", "fontSize") == p_size
    assert css(page, f"{sel} p", "lineHeight") == p_line

    btn = box(page, f"{sel} .btn")
    assert btn["h"] == (42 if device == "mobile" else 56)
    if device == "mobile":
        assert css(page, f"{sel} .topbanner__cta", "flexDirection") == "column"
        assert abs(btn["w"] - (vw - 40)) < 1, "Mobile 按鈕寬度 100%"

    m = box(page, ".topbanner__media")
    if device == "desktop":
        t = box(page, ".topbanner")
        assert t["h"] == 836, "Desktop 高度 = 視窗 900 − header 64"
        assert abs(m["w"] - vw) < 1 and abs(m["h"] - 836) < 1
        assert css(page, ".topbanner__content--desktop", "backgroundColor") == "rgba(0, 0, 0, 0)"
    else:
        ratio = 1640 / 970 if device == "tablet" else 828 / 584
        assert abs(m["w"] / m["h"] - ratio) < 0.01
    # 兩份文字內容相同
    texts = page.eval_on_selector_all(".topbanner__inner h1", "els => els.map(e => e.textContent)")
    assert len(texts) == 2 and texts[0] == texts[1]


# ------------------------------------------------------------------ before-after
@pytest.mark.parametrize("device", DEVICES)
def test_before_after_images_and_handle(open_page, ba_out, device):
    page = open_page(ba_out, device)
    # Before 照片在底層、載入的是 before 素材；After 在上層
    before = page.eval_on_selector(".topbanner__img--before", "e => e.currentSrc")
    after = page.eval_on_selector(".topbanner__img--after", "e => e.currentSrc")
    suffix = {"desktop": "dt", "tablet": "pd", "mobile": "mb"}[device]
    assert before.endswith(f"topbanner-before-{suffix}.jpg"), before
    assert after.endswith(f"topbanner-after-{suffix}.jpg"), after
    assert css(page, ".topbanner__img--after", "clipPath") == "inset(0px 0px 0px 50%)"

    shown = {k: css(page, f".topbanner__handle-img--{k}", "display") for k in ("desktop", "tablet", "mobile")}
    assert [k for k, v in shown.items() if v != "none"] == [device]

    labels = {k: css(page, f".topbanner__label--{k}", "display") for k in ("before", "after")}
    if device == "mobile":
        assert labels == {"before": "block", "after": "block"}
        for k, side in (("before", "left"), ("after", "right")):
            sel = f".topbanner__label--{k}"
            assert css(page, sel, "borderRadius") == "0px"
            assert css(page, sel, "backgroundColor") == "rgba(0, 0, 0, 0.6)"
            assert css(page, sel, "fontSize") == "16px"
            assert css(page, sel, "fontWeight") == "400"
            assert css(page, sel, side) == "0px"
        assert page.inner_text(".topbanner__label--before") == "BEFORE"
    else:
        assert labels == {"before": "none", "after": "none"}


def clip_pct(page):
    v = page.eval_on_selector(".topbanner__img--after", "e => e.style.clipPath")
    return v


def handle_left(page):
    return page.eval_on_selector(".topbanner__handle", "e => e.style.left")


def test_desktop_hover_follows_and_stays(open_page, ba_out):
    page = open_page(ba_out, "desktop")
    m = box(page, ".topbanner__media")
    page.mouse.move(m["x"] + m["w"] * 0.2, m["y"] + m["h"] / 2)
    page.mouse.move(m["x"] + m["w"] * 0.2 + 1, m["y"] + m["h"] / 2)
    assert clip_pct(page).startswith("inset(0px 0px 0px 20"), clip_pct(page)
    assert handle_left(page).startswith("20")
    # 移出區塊（Desktop 區塊高 836，視窗 900，下方 y=880 是區塊外）後，位置維持不動
    page.mouse.move(m["x"] + m["w"] * 0.8, 880)
    assert clip_pct(page).startswith("inset(0px 0px 0px 20"), clip_pct(page)


@pytest.mark.parametrize("device", ["tablet", "mobile"])
def test_touch_devices_click_jumps_and_drag(open_page, ba_out, device):
    page = open_page(ba_out, device)
    m = box(page, ".topbanner__media")
    y = m["y"] + m["h"] / 2
    # 點擊跳到 70%
    page.mouse.click(m["x"] + m["w"] * 0.7, y)
    assert clip_pct(page).startswith("inset(0px 0px 0px 70"), clip_pct(page)
    # 按住拖到 30%
    h = box(page, ".topbanner__handle")
    page.mouse.move(h["x"] + h["w"] / 2, y)
    page.mouse.down()
    page.mouse.move(m["x"] + m["w"] * 0.3, y, steps=5)
    page.mouse.up()
    assert clip_pct(page).startswith("inset(0px 0px 0px 30"), clip_pct(page)
    # 滑鼠只是經過（沒按下）不會改變位置（hover 只在 Desktop）
    page.mouse.move(m["x"] + m["w"] * 0.9, y)
    assert clip_pct(page).startswith("inset(0px 0px 0px 30")


# ------------------------------------------------------------------ standard
@pytest.mark.parametrize("device", DEVICES)
def test_standard_one_video_per_breakpoint(open_page, std_out, device):
    page = open_page(std_out, device)
    suffix = {"desktop": "dt", "tablet": "pd", "mobile": "mb"}[device]
    shown = page.eval_on_selector_all(
        "video.topbanner__video",
        "els => els.filter(e => getComputedStyle(e).display !== 'none').map(e => ({cls: e.className, poster: e.getAttribute('poster')}))",
    )
    assert len(shown) == 1
    assert f"topbanner__video--{device}" in shown[0]["cls"]
    assert shown[0]["poster"].endswith(f"topbanner-poster-{suffix}.jpg")


def test_standard_video_attributes(open_page, std_out):
    page = open_page(std_out, "desktop")
    attrs = page.eval_on_selector_all(
        "video", "els => els.map(e => [e.hasAttribute('autoplay'), e.hasAttribute('loop'), e.muted, e.hasAttribute('playsinline')])"
    )
    assert attrs == [[True, True, True, True]] * 3
    assert page.eval_on_selector_all("video source[media]", "els => els.length") == 0
