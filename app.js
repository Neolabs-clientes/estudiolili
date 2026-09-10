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
    if (!gsapOk || reduce) return;   // sin animacion: el contenido queda visible (CSS por defecto)

    gsap.registerPlugin(ScrollTrigger);

    /* Hero: anima al cargar. fromTo + immediateRender:false => si algo falla,
       el elemento se queda en su estado natural (visible), nunca oculto. */
    var hero = document.querySelector('.hero__copy');
    if (hero) {
      gsap.fromTo(hero.children, { opacity: 0, y: 26 }, {
        opacity: 1, y: 0, duration: 1, ease: 'power3.out', stagger: 0.08, delay: 0.1,
        immediateRender: false, overwrite: true
      });
    }
    var fig = document.querySelector('.hero__figure');
    if (fig) {
      gsap.fromTo(fig, { opacity: 0, scale: 0.95 }, {
        opacity: 1, scale: 1, duration: 1.3, ease: 'power3.out', delay: 0.25,
        immediateRender: false, overwrite: true
      });
    }

    /* Resto de la pagina: por lotes al entrar en pantalla */
    var els = gsap.utils.toArray('.reveal').filter(function (el) { return !el.closest('.hero'); });
    if (els.length) {
      ScrollTrigger.batch(els, {
        start: 'top 94%', once: true,
        onEnter: function (batch) {
          gsap.to(batch, {
            opacity: 1, y: 0, duration: 0.95, ease: 'power3.out', stagger: 0.07, overwrite: true
          });
        },
        onEnterBack: function (batch) {
          gsap.to(batch, { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out', overwrite: true });
        }
      });
      gsap.set(els, { y: 34, opacity: 0 });
      ScrollTrigger.refresh();
    }

    /* Red de seguridad: dentro de la ventana y aun invisible tras 2,5 s => mostrar sin animacion */
    setTimeout(function () {
      els.forEach(function (el) {
        var r = el.getBoundingClientRect();
        var dentro = r.top < window.innerHeight * 0.96 && r.bottom > 0;
        if (dentro && parseFloat(getComputedStyle(el).opacity) < 0.06) {
          el.style.opacity = 1;
          el.style.transform = 'none';
        }
      });
    }, 2500);
  }

  /* ---------- 8. año del pie ---------- */
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
