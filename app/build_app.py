#!/usr/bin/env python3
"""把後台組成單一 HTML 檔：app/dist/topbanner-form.html。

內嵌的內容都從區塊庫與品牌檔讀取（樣式、互動腳本、把手圖），所以後台預覽用的
就是正式流程用的那份檔案；改了區塊樣式後重新執行這支腳本即可。
用法：python app/build_app.py
"""
import base64
import json
import mimetypes
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
APP = REPO / "app"


def data_url(p: Path) -> str:
    mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def read(rel):
    return (REPO / rel).read_text(encoding="utf-8")


def main():
    brand_dir = REPO / "brands" / "yco"
    cfg = yaml.safe_load((brand_dir / "brand.yaml").read_text(encoding="utf-8"))
    files = {}
    for base in ("core/blocks/topbanner", "core/option-group"):
        for p in (REPO / base).rglob("*"):
            if p.suffix in (".css", ".js") and "__pycache__" not in p.parts:
                files[p.relative_to(REPO).as_posix()] = p.read_text(encoding="utf-8")
    ex = {}
    for p in sorted((APP / "example-assets").iterdir()):
        ex[p.name] = {"type": mimetypes.guess_type(p.name)[0], "size": p.stat().st_size, "dataUrl": data_url(p)}
    data = {
        "brand": {
            "css": [read("brands/yco/" + c) for c in cfg["css"]],
            "fonts": cfg.get("fonts", []),
            "assets": {a: data_url(brand_dir / "assets" / a) for a in cfg["assets"]},
        },
        "files": files,
        "example": {
            "heading": "AI Hair Extension Virtual Try-On API",
            "body": "Integrate highly realistic, AI-powered hair extension virtual try-ons into your platform. "
                    "Enable users to seamlessly preview customizable lengths, styles, colors, and bangs on "
                    "user-uploaded images via a streamlined REST API.",
            "files": ex,
        },
    }
    js = "var APP_DATA = " + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + ";"
    tpl = (APP / "index.template.html").read_text(encoding="utf-8")
    out = tpl.replace("/*__DATA__*/", js).replace("/*__RENDER__*/", (APP / "render.js").read_text(encoding="utf-8"))
    dist = APP / "dist"
    dist.mkdir(exist_ok=True)
    (dist / "topbanner-form.html").write_text(out, encoding="utf-8")
    print(f"完成：{dist / 'topbanner-form.html'}（{len(out) / 1024:.0f} KB）")


if __name__ == "__main__":
    main()
