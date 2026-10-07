/* option-group：切換候選版本。
   狀態只存在 .option-group 的 data-active；按鈕點擊只改這個屬性，CSS 負責其餘顯示。
   非顯示中的候選，其影片要暫停（避免背景空轉）；切到該候選時才播放。 */
(function () {
  function videosIn(pane) { return Array.prototype.slice.call(pane.querySelectorAll('video')); }

  function sync(group, active) {
    group.setAttribute('data-active', active);
    group.querySelectorAll('.option-toggle__btn').forEach(function (btn) {
      btn.setAttribute('aria-pressed', btn.getAttribute('data-option-target') === active ? 'true' : 'false');
    });
    group.querySelectorAll(':scope > .option-pane').forEach(function (pane) {
      var on = pane.getAttribute('data-option') === active;
      videosIn(pane).forEach(function (v) {
        if (on) { var p = v.play(); if (p && p.catch) p.catch(function () {}); }
        else { v.pause(); }
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-option-group]').forEach(function (group) {
      sync(group, group.getAttribute('data-active'));
      group.addEventListener('click', function (e) {
        var btn = e.target.closest('.option-toggle__btn');
        if (!btn || !group.contains(btn)) return;
        sync(group, btn.getAttribute('data-option-target'));
      });
    });
  });
})();
