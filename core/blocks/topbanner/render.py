"""Topbanner 區塊的 HTML 產生器。

組裝腳本（tools/build.py）會呼叫 render(content, ctx)。
content 是通過 block.schema.json 驗證的內容資料；ctx 提供：
  ctx.asset(path)        登記專案素材（相對專案資料夾的路徑），回傳頁面上使用的網址
  ctx.brand_asset(name)  登記品牌素材（brands/<brand>/assets/ 內的檔名），回傳網址
回傳 dict：html、css（相對本區塊資料夾的樣式檔）、js（相對本區塊資料夾的腳本檔）。
"""
from html import escape


class BlockError(Exception):
    pass


def _picture(images, ctx, cls, alt):
    """<picture>：≤768px 用 mb、≤1024px 用 pd，其餘用 dt。"""
    return (
        "<picture>\n"
        f'      <source media="(max-width:768px)" srcset="{escape(ctx.asset(images["mb"]))}">\n'
        f'      <source media="(max-width:1024px)" srcset="{escape(ctx.asset(images["pd"]))}">\n'
        f'      <img class="{cls}" src="{escape(ctx.asset(images["dt"]))}" alt="{escape(alt)}">\n'
        "    </picture>"
    )


def _media_before_after(content, ctx):
    before = content["images"]["before"]
    after = content["images"]["after"]
    labels = content.get("labels", {})
    label_before = escape(labels.get("before", "BEFORE"))
    label_after = escape(labels.get("after", "AFTER"))
    return f"""<div class="topbanner__media" id="topbannerMedia">
    <!-- Before 照片：底層，一直都在 -->
    {_picture(before, ctx, "topbanner__img topbanner__img--before", "Before")}
    <!-- After 照片：上層，被拖曳把手裁切 -->
    {_picture(after, ctx, "topbanner__img topbanner__img--after", "After")}
    <!-- 拖曳把手：三張把手圖依斷點顯示其一 -->
    <div class="topbanner__handle" id="topbannerHandle">
      <img class="topbanner__handle-img topbanner__handle-img--desktop" src="{ctx.brand_asset("b_a_sliderContainer.png")}" alt="">
      <img class="topbanner__handle-img topbanner__handle-img--tablet" src="{ctx.brand_asset("b_a_sliderContainer_pd.png")}" alt="">
      <img class="topbanner__handle-img topbanner__handle-img--mobile" src="{ctx.brand_asset("b_a_sliderContainer_mb.png")}" alt="">
    </div>
    <!-- Mobile 專用文字標籤（Desktop/Tablet 的把手圖已內建文字） -->
    <div class="topbanner__label topbanner__label--before">{label_before}</div>
    <div class="topbanner__label topbanner__label--after">{label_after}</div>
  </div>"""


def _video(slot, device, ctx):
    return (
        f'    <video class="topbanner__video topbanner__video--{device}" autoplay loop muted playsinline '
        f'poster="{escape(ctx.asset(slot["poster"]))}">'
        f'<source src="{escape(ctx.asset(slot["video"]))}" type="video/mp4"></video>'
    )


def _media_standard(content, ctx):
    media = content["media"]
    return (
        '<div class="topbanner__media" id="topbannerMedia">\n'
        f'{_video(media["dt"], "desktop", ctx)}\n'
        f'{_video(media["pd"], "tablet", ctx)}\n'
        f'{_video(media["mb"], "mobile", ctx)}\n'
        "  </div>"
    )


def _text_block(content):
    """標題、內文、按鈕。Desktop 與 Tablet/Mobile 各一份（版面不同，用 CSS 切換顯示），
    但內容資料只填一次，由這裡產生兩份。"""
    ctas = ""
    if content.get("ctas"):
        links = "\n".join(
            f'        <a class="btn btn-primary" href="{escape(c.get("href", "#"))}">{escape(c["label"])}</a>'
            for c in content["ctas"]
        )
        ctas = f'\n      <div class="topbanner__cta">\n{links}\n      </div>'
    return (
        '<div class="topbanner__inner">\n'
        f'      <h1>{escape(content["heading"])}</h1>\n'
        f'      <p>{escape(content["body"])}</p>{ctas}\n'
        "    </div>"
    )


MEDIA = {
    "before-after": _media_before_after,
    "standard": _media_standard,
}
VARIANT_FILES = {
    "before-after": {"css": ["variants/before-after/style.css"], "js": ["variants/before-after/behavior.js"]},
    "standard": {"css": ["variants/standard/style.css"], "js": []},
}


def render(content, ctx):
    variant = content["variant"]
    if variant not in MEDIA:
        raise BlockError(f"Topbanner 格式「{variant}」尚未實作（slider 目前只有規範，尚未實測）")
    media_html = MEDIA[variant](content, ctx)
    text = _text_block(content)
    html = f"""<section class="topbanner topbanner--{variant}" id="topbanner" data-block="topbanner" data-variant="{variant}">
  {media_html}
  <!-- Desktop：文字疊在媒體右半 -->
  <div class="topbanner__content topbanner__content--desktop">
    {text}
  </div>
  <!-- Tablet/Mobile：文字在媒體下方（與上面是同一份內容資料） -->
  <div class="topbanner__content topbanner__content--narrow">
    {text}
  </div>
</section>"""
    files = VARIANT_FILES[variant]
    return {"html": html, "css": ["style.css"] + files["css"], "js": files["js"]}
