"""後台（app/render.js）與組裝腳本（tools/build.py）必須產出一樣的頁面。

同一份專案內容，分別交給 Python 組裝腳本和 JS 模組，比對 body 的 HTML、
用到的樣式與腳本檔案。改規則時兩邊要一起改，這個測試會擋住只改一邊。
"""
import json
import shutil
import subprocess

import pytest
import yaml

from conftest import REPO, before_after_block, option_block, run_build, standard_block, write_project

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="需要 Node.js")

CASES = {
    "before-after": lambda: [before_after_block()],
    "standard": lambda: [standard_block()],
    "multiple-ab": lambda: [option_block()],
    "multiple-abc": lambda: [option_block(codes=("a", "b", "c"))],
    "single-use-b": lambda: [option_block(mode="single", use="b")],
    "two-blocks": lambda: [option_block(), standard_block()],
}


def python_side(tmp_path, blocks):
    proj = write_project(tmp_path, blocks)
    out = tmp_path / "out"
    r = run_build(proj, out)
    assert r.returncode == 0, r.stderr
    html = (out / "index.html").read_text(encoding="utf-8")
    start = html.index("<body>\n") + len("<body>\n")
    end = html.rfind("\n\n<script src")
    if end < 0:
        end = html.rfind("\n\n</body>")
    return proj, html[start:end], (out / "style.css").read_text(encoding="utf-8"), (out / "script.js").read_text(encoding="utf-8") if (out / "script.js").exists() else ""


def js_side(proj, tmp_path):
    data = yaml.safe_load(proj.read_text(encoding="utf-8"))
    pj = tmp_path / "project.json"
    pj.write_text(json.dumps(data), encoding="utf-8")
    r = subprocess.run([NODE, str(REPO / "app" / "render_cli.js"), str(pj)], capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stdout + r.stderr
    return json.loads(r.stdout)


def read(p):
    return (REPO / p).read_text(encoding="utf-8")


@pytest.mark.parametrize("name", list(CASES))
def test_js_matches_python(tmp_path, name):
    proj, py_body, py_css, py_js = python_side(tmp_path, CASES[name]())
    js = js_side(proj, tmp_path)
    assert js["body"] == py_body
    brand_css = "\n".join(read("brands/yco/" + c) for c in ["tokens.css", "base.css", "components/button.css"])
    assert "\n".join([brand_css] + [read(p) for p in js["cssFiles"]]) == py_css
    assert "\n".join(read(p) for p in js["jsFiles"]) == py_js


@pytest.mark.parametrize("bad", [
    {"block": "topbanner", "mode": "multiple", "options": {"a": {"label": "x"}}},
    {"block": "topbanner", "mode": "single", "options": {"a": {}}},
    {"block": "topbanner", "mode": "both", "options": {"a": {}, "b": {}}},
])
def test_js_reports_same_option_errors(tmp_path, bad):
    proj = write_project(tmp_path, [bad])
    r = run_build(proj, tmp_path / "out")
    assert r.returncode == 1
    (tmp_path / "p.json").write_text(json.dumps({"project": "x", "brand": "yco", "blocks": [bad]}), encoding="utf-8")
    js = subprocess.run([NODE, str(REPO / "app" / "render_cli.js"), str(tmp_path / "p.json")], capture_output=True, text=True, encoding="utf-8")
    assert js.returncode == 2
    msg = json.loads(js.stdout)["error"]
    # 兩邊的問題清單（去掉標題行）要一樣
    py_lines = [l.strip() for l in r.stderr.splitlines() if l.strip().startswith("- ")]
    js_lines = [l.strip() for l in msg.splitlines() if l.strip().startswith("- ")]
    assert py_lines == js_lines
