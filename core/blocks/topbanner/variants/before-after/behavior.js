/* ==========================================================================
   Topbanner — before-after 互動
   來源：舊流程 DESIGN-RULES.md §5.10「拖曳互動邏輯」、現有頁面 script.js。

   兩套互動模式共用同一個函式：
   - Desktop（≥1025px）：hover 直接跟隨。滑鼠移進整個 Topbanner 範圍，不需要按住，
     X 座標即時帶動把手；離開後停在最後位置。原因：Desktop 文字疊在媒體右半，
     與把手是同層元素，把手跑到右半會被文字區塊擋住滑鼠事件，所以改用整個區塊感應。
   - Tablet/Mobile：mousedown/touchstart 按住把手拖曳，也可以點媒體任一處直接跳過去。

   名稱說明：clipLayer 是「被裁切的那一層」，裡面裝的是 After 照片
   （class 為 .topbanner__img--after）；底層是 Before 照片。
   ========================================================================== */
(function () {
  function initCompare(container, handle, clipLayer, opts) {
    opts = opts || {};
    var hoverSection = opts.hoverSection || null;
    var hoverMinWidth = opts.hoverMinWidth || 1025;
    var dragging = false;

    function setPct(clientX) {
      var rect = container.getBoundingClientRect();
      var pct = ((clientX - rect.left) / rect.width) * 100;
      pct = Math.max(0, Math.min(100, pct));
      handle.style.left = pct + '%';
      clipLayer.style.clipPath = 'inset(0 0 0 ' + pct + '%)';
    }

    function isHoverMode() {
      return hoverSection && window.innerWidth >= hoverMinWidth;
    }

    if (hoverSection) {
      hoverSection.addEventListener('mousemove', function (e) {
        if (isHoverMode()) setPct(e.clientX);
      });
    }

    handle.addEventListener('mousedown', function (e) {
      if (isHoverMode()) return;
      dragging = true; e.preventDefault();
    });
    handle.addEventListener('touchstart', function () { dragging = true; }, { passive: true });

    window.addEventListener('mousemove', function (e) {
      if (dragging && !isHoverMode()) setPct(e.clientX);
    });
    window.addEventListener('touchmove', function (e) {
      if (dragging && e.touches[0]) setPct(e.touches[0].clientX);
    }, { passive: true });

    window.addEventListener('mouseup', function () { dragging = false; });
    window.addEventListener('touchend', function () { dragging = false; });

    container.addEventListener('click', function (e) {
      if (isHoverMode()) return;
      if (e.target === handle || handle.contains(e.target)) return;
      setPct(e.clientX);
    });
  }

  // 頁面上可能有多個 Topbanner（例如複數選擇的多個候選），所以逐一初始化，不依賴固定 id
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.topbanner--before-after').forEach(function (section) {
      var media = section.querySelector('.topbanner__media');
      var handle = section.querySelector('.topbanner__handle');
      var clipLayer = section.querySelector('.topbanner__img--after');
      if (media && handle && clipLayer) {
        initCompare(media, handle, clipLayer, { hoverSection: section, hoverMinWidth: 1025 });
      }
    });
  });
})();
