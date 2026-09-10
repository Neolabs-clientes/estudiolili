/* =====================================================================
   Estudio de uñas Lili · interacciones de página
   WhatsApp, navegación, galería, formulario y animaciones de entrada
   ===================================================================== */
(function () {
  'use strict';

  /* ---------- 1. WhatsApp ---------- */
  var WA_NUM = '34681861137';
  var WA = function (msg) {
    return 'https://wa.me/' + WA_NUM + (msg ? '?text=' + encodeURIComponent(msg) : '');
  };
  var WA_DEFAULT = 'Hola Lili, me gustaría pedir cita para las uñas.';

  document.querySelectorAll('[data-wa]').forEach(function (el) {
    el.setAttribute('href', WA(el.getAttribute('data-wa')));
    el.setAttribute('target', '_blank');
    el.setAttribute('rel', 'noopener');
  });
  var bubble = document.getElementById('wa-bubble');
  if (bubble) {
    bubble.setAttribute('href', WA(WA_DEFAULT));
    bubble.setAttribute('target', '_blank');
    bubble.setAttribute('rel', 'noopener');
  }

  /* ---------- 2. preloader ---------- */
  var loader = document.getElementById('loader');
  var hideLoader = function () {
    if (!loader || loader.classList.contains('is-done')) return;
    loader.classList.add('is-done');
    document.body.classList.remove('is-loading');
    startReveals();
  };
  window.addEventListener('load', function () { setTimeout(hideLoader, 420); });
  setTimeout(hideLoader, 2600);           // red de seguridad

  /* ---------- 3. navegación ---------- */
  var nav = document.getElementById('nav');
  var onScroll = function () {
    if (nav) nav.classList.toggle('is-stuck', window.scrollY > 42);
  };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ---------- 4. scroll suave en anclas ---------- */
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    var id = a.getAttribute('href');
    if (!id || id === '#') return;
    a.addEventListener('click', function (e) {
      var t = document.querySelector(id);
      if (!t) return;
      e.preventDefault();
      t.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
    });
  });

  /* ---------- 5. galería con lightbox ---------- */
  var lb = document.getElementById('lightbox');
  var lbImg = document.getElementById('lightbox-img');
  document.querySelectorAll('.shot').forEach(function (shot) {
    shot.addEventListener('click', function (e) {
      e.preventDefault();
      if (!lb || !lbImg) return;
      lbImg.src = shot.getAttribute('data-full') || shot.getAttribute('href');
      lbImg.alt = (shot.querySelector('img') || {}).alt || '';
      lb.hidden = false;
      document.body.style.overflow = 'hidden';
    });
  });
  var closeLb = function () {
    if (!lb) return;
    lb.hidden = true;
    if (lbImg) lbImg.src = '';
    document.body.style.overflow = '';
  };
  if (lb) {
    lb.addEventListener('click', function (e) {
      if (e.target === lb || e.target.id === 'lightbox-close') closeLb();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !lb.hidden) closeLb();
    });
  }

  /* ---------- 6. formulario -> WhatsApp ---------- */
  var form = document.getElementById('form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var g = function (id) { var el = document.getElementById(id); return el ? el.value.trim() : ''; };
      var nombre = g('f-nombre'), tel = g('f-tel'), servicio = g('f-servicio'),
          fecha = g('f-fecha'), msg = g('f-msg');
      var bad = false;
      [['f-nombre', nombre.length > 1], ['f-tel', tel.replace(/\D/g, '').length >= 6]].forEach(function (p) {
        var el = document.getElementById(p[0]);
        if (!el) return;
        el.classList.toggle('is-bad', !p[1]);
        if (!p[1]) bad = true;
      });
      if (bad) return;
      var texto = 'Hola Lili, quiero pedir cita.\n'
        + '- Nombre: ' + nombre + '\n'
        + '- Teléfono: ' + tel + '\n'
        + '- Servicio: ' + servicio + '\n'
        + (fecha ? '- Cuándo: ' + fecha + '\n' : '')
        + (msg ? '- Comentario: ' + msg + '\n' : '')
        + '\n(Enviado desde la web)';
      window.open(WA(texto), '_blank', 'noopener');
      var ok = document.getElementById('form-ok');
      if (ok) ok.hidden = false;
      form.reset();
    });
  }

  /* ---------- 7. animaciones de entrada ---------- */
  var started = false;
  function startReveals() {
    if (started) return;
    started = true;
    var gsapOk = typeof window.gsap !== 'undefined' && typeof window.ScrollTrigger !== 'undefined';
    if (!gsapOk || reduce) {
      document.querySelectorAll('.reveal').forEach(function (el) { el.style.opacity = 1; });
      return;
    }
    gsap.registerPlugin(ScrollTrigger);
    gsap.utils.toArray('.reveal').forEach(function (el) {
      gsap.from(el, {
        opacity: 0, y: 34, duration: 1, ease: 'power3.out',
        scrollTrigger: { trigger: el, start: 'top 88%', once: true }
      });
    });
    // hero
    var hero = document.querySelector('.hero__copy');
    if (hero) {
      gsap.from(hero.children, {
        opacity: 0, y: 26, duration: 1.1, ease: 'power3.out',
        stagger: 0.09, delay: 0.15
      });
    }
    var fig = document.querySelector('.hero__figure');
    if (fig) {
      gsap.from(fig, { opacity: 0, scale: 0.94, duration: 1.4, ease: 'power3.out', delay: 0.3 });
    }
    ScrollTrigger.refresh();
  }

  /* ---------- 8. año del pie ---------- */
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
