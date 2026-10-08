
document.addEventListener('DOMContentLoaded', function () {
  var hamburgerBtn = document.getElementById('hamburgerBtn');
  var drawer = document.getElementById('mobileDrawer');
  var drawerClose = document.getElementById('drawerClose');
  var drawerBackdrop = document.getElementById('drawerBackdrop');
  function openDrawer() { drawer.classList.add('is-open'); }
  function closeDrawer() {
    drawer.classList.remove('is-open');
    document.querySelectorAll('.mobile-submenu.is-open').forEach(function (p) {
      p.classList.remove('is-open');
    });
  }
  if (hamburgerBtn) hamburgerBtn.addEventListener('click', openDrawer);
  if (drawerClose) drawerClose.addEventListener('click', closeDrawer);
  if (drawerBackdrop) drawerBackdrop.addEventListener('click', closeDrawer);
  document.querySelectorAll('[data-submenu]').forEach(function (item) {
    item.addEventListener('click', function () {
      var key = item.getAttribute('data-submenu');
      var panel = document.querySelector('[data-submenu-panel="' + key + '"]');
      if (panel) panel.classList.add('is-open');
    });
  });
  document.querySelectorAll('.mobile-submenu__back').forEach(function (btn) {
    btn.addEventListener('click', function () {
      btn.closest('.mobile-submenu').classList.remove('is-open');
    });
  });
  var langSwitch = document.getElementById('langSwitch');
  var langBtn = document.getElementById('langBtn');
  if (langBtn) {
    langBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      langSwitch.classList.toggle('is-open');
    });
    document.addEventListener('click', function () {
      langSwitch.classList.remove('is-open');
    });
    langSwitch.querySelectorAll('.lang-switch__list button').forEach(function (b) {
      b.addEventListener('click', function () {
        var hiddenLabel = langBtn.querySelector('.visually-hidden');
        if (hiddenLabel) hiddenLabel.textContent = b.textContent;
        langBtn.setAttribute('aria-label', 'Language: ' + b.textContent);
        langSwitch.classList.remove('is-open');
      });
    });
  }
  var copyrightEl = document.getElementById('copyright');
  if (copyrightEl) {
    copyrightEl.textContent = '© ' + new Date().getFullYear() + ' Perfect Corp. All Rights Reserved.';
  }
  function initBeforeAfter(container, handle, beforeImg, opts) {
    opts = opts || {};
    var hoverSection = opts.hoverSection || null;
    var hoverMinWidth = opts.hoverMinWidth || 1025;
    var dragging = false;
    function setPct(clientX) {
      var rect = container.getBoundingClientRect();
      var pct = ((clientX - rect.left) / rect.width) * 100;
      pct = Math.max(0, Math.min(100, pct));
      handle.style.left = pct + '%';
      beforeImg.style.clipPath = 'inset(0 0 0 ' + pct + '%)';
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
      if (isHoverMode()) return; // Desktop 已經用 hover 追蹤，不需要另外拖曳
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
  document.querySelectorAll('.zz-ba').forEach(function (zzContainer) {
    var zzHandle = zzContainer.querySelector('.zz-ba__handle');
    var zzBefore = zzContainer.querySelector('.zz-ba__img--before');
    if (zzHandle && zzBefore) initBeforeAfter(zzContainer, zzHandle, zzBefore);
  });
  var tbSection = document.getElementById('topbanner');
  if (tbSection) {
    var tbButtons = tbSection.querySelectorAll('.topbanner__toggle-option');
    var tbVideos = tbSection.querySelectorAll('.topbanner__video');
    var setTopbannerVariant = function (v) {
      tbSection.setAttribute('data-topbanner-variant', v);
      tbButtons.forEach(function (b) {
        b.setAttribute('aria-pressed', b.getAttribute('data-variant') === v ? 'true' : 'false');
      });
      tbVideos.forEach(function (video) {
        var poster = video.getAttribute('data-poster-' + v);
        var source = video.querySelector('source');
        var src = source ? source.getAttribute('data-src-' + v) : null;
        if (poster) video.setAttribute('poster', poster);
        if (source && src) source.setAttribute('src', src);
        video.load();
        var p = video.play();
        if (p && p.catch) p.catch(function () {});
      });
    };
    tbButtons.forEach(function (b) {
      b.addEventListener('click', function () {
        var v = b.getAttribute('data-variant');
        if (v && v !== tbSection.getAttribute('data-topbanner-variant')) setTopbannerVariant(v);
      });
    });
  }
  var faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach(function (item) {
    var q = item.querySelector('.faq-item__q');
    var a = item.querySelector('.faq-item__a');
    var icon = item.querySelector('.faq-item__q img');
    if (item.classList.contains('is-open')) {
      a.style.maxHeight = a.scrollHeight + 'px';
    }
    q.addEventListener('click', function () {
      var willOpen = !item.classList.contains('is-open');
      faqItems.forEach(function (other) {
        other.classList.remove('is-open');
        other.querySelector('.faq-item__a').style.maxHeight = null;
        other.querySelector('.faq-item__q img').src = 'assets/YCO/icons/Icon_close.svg';
      });
      if (willOpen) {
        item.classList.add('is-open');
        a.style.maxHeight = a.scrollHeight + 'px';
        icon.src = 'assets/YCO/icons/Icon_open.svg';
      }
    });
  });
});
