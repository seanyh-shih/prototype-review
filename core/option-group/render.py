"""複數選擇（option-group）的 HTML 產生器：切換按鈕與外層容器。

組裝腳本（tools/build.py）呼叫。各候選的內容由對應區塊自己的 render 產生，
這裡只負責把它們包進 .option-group，並提供各區塊可以放置的切換按鈕。
"""
from html import escape

OPTION_CODES = ("a", "b", "c")   # 候選代號，順序即按鈕順序；最多 3 個


def toggle_html(codes, kind, labels=None):
    """kind：'overlay'（疊在媒體上，Desktop）或 'inline'（跟標題同列，Tablet/Mobile）。"""
    labels = labels or {}
    btns = "".join(
        f'<button type="button" class="option-toggle__btn" data-option-target="{c}" '
        f'aria-pressed="false" title="{escape(labels.get(c, ""))}">{c.upper()}</button>'
        for c in codes
    )
    return f'<div class="option-toggle option-toggle--{kind}" role="group" aria-label="切換版本">{btns}</div>'


def toggles(codes, labels=None):
    return {"overlay": toggle_html(codes, "overlay", labels), "inline": toggle_html(codes, "inline", labels)}


def wrap(panes):
    """panes：[(代號, 區塊 html), ...]，預設顯示第一個。"""
    inner = "\n".join(
        f'<div class="option-pane" data-option="{c}">\n{html}\n</div>' for c, html in panes
    )
    return f'<div class="option-group" data-option-group data-active="{panes[0][0]}">\n{inner}\n</div>'
