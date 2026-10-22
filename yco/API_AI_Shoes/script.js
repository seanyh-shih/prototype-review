
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
