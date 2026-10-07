"""組裝腳本：錯誤訊息、輸出結構、覆蓋保護。"""
import copy

from conftest import REPO, before_after_block, run_build, standard_block, write_project


def test_build_before_after_structure(tmp_path):
    proj = write_project(tmp_path, [before_after_block()])
    out = tmp_path / "out"
    r = run_build(proj, out)
    assert r.returncode == 0, r.stderr
    for f in ["index.html", "style.css", "script.js", ".prototype-system-build"]:
        assert (out / f).exists(), f
    assert (out / "assets" / "brand" / "b_a_sliderContainer.png").exists()
    assert (out / "assets" / "topbanner-before-dt.jpg").exists()
    html = (out / "index.html").read_text(encoding="utf-8")
    assert 'data-variant="before-after"' in html
    assert " id=" not in html, "區塊不能輸出 id，否則同頁多個候選會重複"


def test_build_standard_has_no_script(tmp_path):
    proj = write_project(tmp_path, [standard_block()])
    out = tmp_path / "out"
    assert run_build(proj, out).returncode == 0
    assert not (out / "script.js").exists()
    html = (out / "index.html").read_text(encoding="utf-8")
    assert html.count("<video") == 3
    assert "<source media" not in html, "<video> 內不可用 <source media>"


def test_brand_required(tmp_path):
    proj = write_project(tmp_path, [before_after_block()])
    text = proj.read_text(encoding="utf-8").replace("brand: yco\n", "")
    proj.write_text(text, encoding="utf-8")
    r = run_build(proj, tmp_path / "out")
    assert r.returncode == 1
    assert "brand" in r.stderr and "沒有預設值" in r.stderr


def test_unknown_brand(tmp_path):
    proj = write_project(tmp_path, [before_after_block()], brand="abc")
    r = run_build(proj, tmp_path / "out")
    assert r.returncode == 1 and "不認得的品牌" in r.stderr


def test_pfcom_needs_segment_then_not_built(tmp_path):
    proj = write_project(tmp_path, [before_after_block()], brand="pfcom")
    r = run_build(proj, tmp_path / "out")
    assert r.returncode == 1 and "segment" in r.stderr
    proj = write_project(tmp_path, [before_after_block()], brand="pfcom", segment="2c")
    r = run_build(proj, tmp_path / "out")
    assert r.returncode == 1 and "尚未建立" in r.stderr


def test_missing_field_message_is_chinese(tmp_path):
    b = before_after_block()
    del b["heading"]
    r = run_build(write_project(tmp_path, [b]), tmp_path / "out")
    assert r.returncode == 1
    assert "缺少必填欄位「heading」" in r.stderr
    assert "Unevaluated" not in r.stderr and "oneOf" not in r.stderr


def test_wrong_variant_fields_message(tmp_path):
    b = before_after_block()
    b["media"] = standard_block()["media"]
    r = run_build(write_project(tmp_path, [b]), tmp_path / "out")
    assert r.returncode == 1
    assert "media" in r.stderr and "不屬於" in r.stderr


def test_missing_asset_file_reported(tmp_path):
    proj = write_project(tmp_path, [before_after_block()])
    (tmp_path / "assets" / "topbanner-after-mb.jpg").unlink()
    r = run_build(proj, tmp_path / "out")
    assert r.returncode == 1 and "topbanner-after-mb.jpg" in r.stderr


def test_slider_not_implemented_message(tmp_path):
    b = copy.deepcopy(before_after_block())
    for k in ("images",):
        del b[k]
    b["variant"] = "slider"
    b["slides"] = [{"images": {d: f"assets/topbanner-before-{d}.jpg" for d in ("dt", "pd", "mb")}, "prompt": "p"}] * 3
    r = run_build(write_project(tmp_path, [b]), tmp_path / "out")
    assert r.returncode == 1 and "尚未實作" in r.stderr


def test_refuses_to_overwrite_foreign_folder(tmp_path):
    proj = write_project(tmp_path, [before_after_block()])
    out = tmp_path / "out"
    out.mkdir()
    (out / "mine.txt").write_text("別刪我", encoding="utf-8")
    r = run_build(proj, out)
    assert r.returncode == 1 and "不會覆蓋" in r.stderr
    assert (out / "mine.txt").exists()


def test_rebuild_over_previous_build_ok(tmp_path):
    proj = write_project(tmp_path, [before_after_block()])
    out = tmp_path / "out"
    assert run_build(proj, out).returncode == 0
    assert run_build(proj, out).returncode == 0
