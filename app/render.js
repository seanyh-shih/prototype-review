/* 產生頁面的共用模組（瀏覽器與 Node 都能用，不碰 DOM）。
   規則與 core/blocks/topbanner/render.py、core/option-group/render.py、tools/build.py 一致；
   tests/test_app_render.py 會用同一份內容比對兩邊的輸出，改一邊就要改另一邊。 */
(function (root) {
  'use strict';

  var OPTION_CODES = ['a', 'b', 'c'];

  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#x27;');
  }

  // ---------------------------------------------------------------- 複數選擇
  function toggleHtml(codes, kind, labels) {
    labels = labels || {};
    var btns = codes.map(function (c) {
      return '<button type="button" class="option-toggle__btn" data-option-target="' + c + '" ' +
        'aria-pressed="false" title="' + esc(labels[c] || '') + '">' + c.toUpperCase() + '</button>';
    }).join('');
    return '<div class="option-toggle option-toggle--' + kind + '" role="group" aria-label="切換版本">' + btns + '</div>';
  }
  function toggles(codes, labels) {
    return { overlay: toggleHtml(codes, 'overlay', labels), inline: toggleHtml(codes, 'inline', labels) };
  }
  function wrap(panes) {
    var inner = panes.map(function (p) {
      return '<div class="option-pane" data-option="' + p[0] + '">\n' + p[1] + '\n</div>';
    }).join('\n');
    return '<div class="option-group" data-option-group data-active="' + panes[0][0] + '">\n' + inner + '\n</div>';
  }

  // ---------------------------------------------------------------- Topbanner
  function picture(images, ctx, cls, alt) {
    return '<picture>\n' +
      '      <source media="(max-width:768px)" srcset="' + esc(ctx.asset(images.mb)) + '">\n' +
      '      <source media="(max-width:1024px)" srcset="' + esc(ctx.asset(images.pd)) + '">\n' +
      '      <img class="' + cls + '" src="' + esc(ctx.asset(images.dt)) + '" alt="' + esc(alt) + '">\n' +
      '    </picture>';
  }
  function mediaBeforeAfter(content, ctx) {
    var before = content.images.before, after = content.images.after;
    var labels = content.labels || {};
    var lb = esc(labels.before != null ? labels.before : 'BEFORE');
    var la = esc(labels.after != null ? labels.after : 'AFTER');
    return '<div class="topbanner__media">\n' +
      '    <!-- Before 照片：底層，一直都在 -->\n' +
      '    ' + picture(before, ctx, 'topbanner__img topbanner__img--before', 'Before') + '\n' +
      '    <!-- After 照片：上層，被拖曳把手裁切 -->\n' +
      '    ' + picture(after, ctx, 'topbanner__img topbanner__img--after', 'After') + '\n' +
      '    <!-- 拖曳把手：三張把手圖依斷點顯示其一 -->\n' +
      '    <div class="topbanner__handle">\n' +
      '      <img class="topbanner__handle-img topbanner__handle-img--desktop" src="' + ctx.brandAsset('b_a_sliderContainer.png') + '" alt="">\n' +
      '      <img class="topbanner__handle-img topbanner__handle-img--tablet" src="' + ctx.brandAsset('b_a_sliderContainer_pd.png') + '" alt="">\n' +
      '      <img class="topbanner__handle-img topbanner__handle-img--mobile" src="' + ctx.brandAsset('b_a_sliderContainer_mb.png') + '" alt="">\n' +
      '    </div>\n' +
      '    <!-- Mobile 專用文字標籤（Desktop/Tablet 的把手圖已內建文字） -->\n' +
      '    <div class="topbanner__label topbanner__label--before">' + lb + '</div>\n' +
      '    <div class="topbanner__label topbanner__label--after">' + la + '</div>\n' +
      '  </div>';
  }
  function video(slot, device, ctx) {
    return '    <video class="topbanner__video topbanner__video--' + device + '" autoplay loop muted playsinline ' +
      'poster="' + esc(ctx.asset(slot.poster)) + '">' +
      '<source src="' + esc(ctx.asset(slot.video)) + '" type="video/mp4"></video>';
  }
  function mediaStandard(content, ctx) {
    var m = content.media;
    return '<div class="topbanner__media">\n' +
      video(m.dt, 'desktop', ctx) + '\n' +
      video(m.pd, 'tablet', ctx) + '\n' +
      video(m.mb, 'mobile', ctx) + '\n' +
      '  </div>';
  }
  function textBlock(content, inlineToggle) {
    var ctas = '';
    if (content.ctas && content.ctas.length) {
      var links = content.ctas.map(function (c) {
        return '        <a class="btn btn-primary" href="' + esc(c.href != null ? c.href : '#') + '">' + esc(c.label) + '</a>';
      }).join('\n');
      ctas = '\n      <div class="topbanner__cta">\n' + links + '\n      </div>';
    }
    var h1 = '<h1>' + esc(content.heading) + '</h1>';
    if (inlineToggle) h1 = '<div class="topbanner__heading-row">' + h1 + inlineToggle + '</div>';
    return '<div class="topbanner__inner">\n' +
      '      ' + h1 + '\n' +
      '      <p>' + esc(content.body) + '</p>' + ctas + '\n' +
      '    </div>';
  }
  var MEDIA = { 'before-after': mediaBeforeAfter, 'standard': mediaStandard };
  var VARIANT_FILES = {
    'before-after': { css: ['variants/before-after/style.css'], js: ['variants/before-after/behavior.js'] },
    'standard': { css: ['variants/standard/style.css'], js: [] }
  };

  function renderTopbanner(content, ctx, toggle) {
    var variant = content.variant;
    if (!MEDIA[variant]) throw new Error('Topbanner 格式「' + variant + '」尚未實作（slider 目前只有規範，尚未實測）');
    var mediaHtml = MEDIA[variant](content, ctx);
    toggle = toggle || {};
    var tDesktop = textBlock(content, '');
    var tNarrow = textBlock(content, toggle.inline || '');
    var html = '<section class="topbanner topbanner--' + variant + '" data-block="topbanner" data-variant="' + variant + '">\n' +
      '  ' + mediaHtml + '\n' +
      '  <!-- Desktop：文字疊在媒體右半 -->\n' +
      '  <div class="topbanner__content topbanner__content--desktop">\n' +
      '    ' + tDesktop + '\n' +
      '  </div>\n' +
      '  ' + (toggle.overlay || '') + '\n' +
      '  <!-- Tablet/Mobile：文字在媒體下方（與上面是同一份內容資料） -->\n' +
      '  <div class="topbanner__content topbanner__content--narrow">\n' +
      '    ' + tNarrow + '\n' +
      '  </div>\n' +
      '</section>';
    var f = VARIANT_FILES[variant];
    return { html: html, css: ['core/blocks/topbanner/style.css'].concat(f.css.map(function (p) { return 'core/blocks/topbanner/' + p; })),
             js: f.js.map(function (p) { return 'core/blocks/topbanner/' + p; }) };
  }

  var BLOCKS = { topbanner: { render: renderTopbanner, supportsToggle: true } };

  // ---------------------------------------------------------------- 專案
  // 錯誤訊息裡顯示的值，格式與 Python 版（repr）一致，兩邊訊息才會相同
  function pyRepr(v) { return v == null ? 'None' : typeof v === 'string' ? "'" + v + "'" : String(v); }
  var WRAPPER_KEYS = ['block', 'mode', 'use', 'options'];

  function expandEntry(content, label, problems) {
    if (!content || typeof content !== 'object' || !('block' in content)) {
      problems.push(label + '：缺少 block 欄位（區塊 ID，例如 topbanner）。'); return null;
    }
    if (!('mode' in content) && !('options' in content) && !('use' in content)) {
      return ['single', [[null, null, content]]];
    }
    var where = label + '（' + content.block + '）';
    var extra = Object.keys(content).filter(function (k) { return WRAPPER_KEYS.indexOf(k) < 0; }).sort();
    if (extra.length) { problems.push(where + '：使用 mode／options 時，內容必須寫在各候選（options 底下）裡，不能直接寫在外層：' + extra.join('、')); return null; }
    var mode = 'mode' in content ? content.mode : 'single';
    if (mode !== 'single' && mode !== 'multiple') { problems.push(where + '：mode 必須是 single（單一選擇）或 multiple（複數選擇），目前是 ' + pyRepr(mode) + '。'); return null; }
    var options = content.options;
    if (!options || typeof options !== 'object' || !Object.keys(options).length) { problems.push(where + '：缺少 options（候選內容），格式為 a:、b:、c: 各一份。'); return null; }
    var bad = Object.keys(options).filter(function (k) { return OPTION_CODES.indexOf(k) < 0; });
    if (bad.length) { problems.push(where + '：候選代號只能用 ' + OPTION_CODES.join('、') + '，不認得：' + bad.join('、') + '。'); return null; }
    var codes = OPTION_CODES.filter(function (c) { return c in options; });
    function opt(c) {
      var body = {};
      Object.keys(options[c]).forEach(function (k) { if (k !== 'label') body[k] = options[c][k]; });
      body.block = content.block;
      return [c, options[c].label, body];
    }
    if (mode === 'single') {
      if (!(content.use in options)) { problems.push(where + '：單一選擇必須用 use 指定採用哪一個候選（' + codes.join('、') + '），目前是 ' + pyRepr(content.use) + '。'); return null; }
      return ['single', [opt(content.use)]];
    }
    if ('use' in content) { problems.push(where + '：複數選擇會輸出全部候選，不需要 use；若要只採用其中一個，請改成 mode: single。'); return null; }
    if (codes.length < 2) { problems.push(where + '：複數選擇至少需要 2 個候選（目前只有 ' + codes.length + ' 個）。只有一個版本請改用單一選擇。'); return null; }
    return ['multiple', codes.map(opt)];
  }

  /* 組出頁面各部分。ctx：{asset(rel), brandAsset(name)}。
     回傳 { body, cssFiles, jsFiles, multipleCount }；內容有問題時丟出 Error（訊息為中文清單）。 */
  function buildParts(project, ctx) {
    var problems = [], parts = [], css = [], js = [], multipleCount = 0;
    function add(list, items) { items.forEach(function (p) { if (list.indexOf(p) < 0) list.push(p); }); }
    function one(content, label, toggle) {
      var blk = BLOCKS[content.block];
      if (!blk) { problems.push(label + '：不認得的區塊「' + content.block + '」。'); return null; }
      try { return blk.render(content, ctx, toggle); } catch (e) { problems.push(label + '：' + e.message); return null; }
    }
    (project.blocks || []).forEach(function (content, i) {
      var label = '第 ' + (i + 1) + ' 個區塊';
      var ex = expandEntry(content, label, problems);
      if (!ex) return;
      var mode = ex[0], options = ex[1], blockId = content.block;
      if (mode === 'single') {
        var o = options[0];
        var r = one(o[2], label + '（' + blockId + (o[0] ? '，候選 ' + o[0] : '') + '）', null);
        if (r) { parts.push(r.html); add(css, r.css); add(js, r.js); }
        return;
      }
      var codes = options.map(function (o) { return o[0]; });
      var labels = {};
      options.forEach(function (o) { if (o[1]) labels[o[0]] = o[1]; });
      var panes = [], ok = true;
      options.forEach(function (o) {
        var r = one(o[2], label + '（' + blockId + '，候選 ' + o[0] + '）', toggles(codes, labels));
        if (!r) { ok = false; return; }
        panes.push([o[0], r.html]); add(css, r.css); add(js, r.js);
      });
      if (ok) { parts.push(wrap(panes)); multipleCount++; }
    });
    if (problems.length) throw new Error('內容有以下問題，請修正後再執行：\n  - ' + problems.join('\n  - '));
    if (multipleCount) { css.push('core/option-group/style.css'); js.push('core/option-group/behavior.js'); }
    var body = parts.join('\n\n');
    if (multipleCount) {
      body = '<div class="review-banner" data-review-banner>評審版：含 ' + multipleCount + ' 個比較區塊，不是正式版</div>\n\n' + body;
    }
    return { body: body, cssFiles: css, jsFiles: js, multipleCount: multipleCount };
  }

  /* 把各部分組成單一 HTML 檔（樣式、腳本都內嵌）。files：{ 'core/…/style.css': 文字 }，brandCss：品牌樣式（依序）。 */
  function assemblePage(project, parts, files, brand) {
    var css = brand.css.concat(parts.cssFiles.map(function (p) { return files[p]; })).join('\n');
    var js = parts.jsFiles.map(function (p) { return files[p]; }).join('\n');
    var fonts = brand.fonts.length
      ? '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n' +
        brand.fonts.map(function (u) { return '<link href="' + esc(u) + '" rel="stylesheet">'; }).join('\n')
      : '';
    var title = esc(project.title || project.project);
    return '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n' +
      '<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>' + title + '</title>\n' + fonts + '\n' +
      '<style>\n' + css + '\n</style>\n</head>\n<body>\n' + parts.body + '\n' +
      (js ? '<script>\n' + js.replace(/<\/script/gi, '<\\/script') + '\n<\/script>\n' : '') + '</body>\n</html>\n';
  }

  /* 專案資料 → YAML（只處理我們的資料型態：物件、陣列、字串、數字、布林）。字串一律用雙引號。 */
  function toYaml(v, indent) {
    indent = indent || 0;
    var pad = new Array(indent + 1).join(' ');
    if (Array.isArray(v)) {
      return v.map(function (item) {
        if (item && typeof item === 'object') {
          var inner = toYaml(item, indent + 2).replace(/^\s+/, '');
          return pad + '- ' + inner;
        }
        return pad + '- ' + scalar(item);
      }).join('\n');
    }
    return Object.keys(v).map(function (k) {
      var x = v[k];
      if (x && typeof x === 'object') {
        if (Array.isArray(x) ? !x.length : !Object.keys(x).length) return pad + k + ': ' + (Array.isArray(x) ? '[]' : '{}');
        return pad + k + ':\n' + toYaml(x, indent + 2);
      }
      return pad + k + ': ' + scalar(x);
    }).join('\n');
  }
  function scalar(x) { return typeof x === 'string' ? JSON.stringify(x) : String(x); }

  var api = { esc: esc, buildParts: buildParts, assemblePage: assemblePage, toYaml: toYaml, OPTION_CODES: OPTION_CODES };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.PFRender = api;
})(typeof window !== 'undefined' ? window : globalThis);
