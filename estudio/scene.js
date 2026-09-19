/* =====================================================================
   Estudio de uñas Lili · capa WebGL
   Partículas doradas + nudo satinado con bloom (three.js self-hosted)
   ===================================================================== */
import * as THREE from './vendor/three.module.js';
import { EffectComposer } from './vendor/postprocessing/EffectComposer.js';
import { RenderPass } from './vendor/postprocessing/RenderPass.js';
import { UnrealBloomPass } from './vendor/postprocessing/UnrealBloomPass.js';
import { OutputPass } from './vendor/postprocessing/OutputPass.js';

const canvas = document.getElementById('gl');
const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const MOBILE = window.matchMedia('(max-width: 820px)').matches;

function heroBox() {
  const bg = document.querySelector('.hero__bg');
  const w = (bg && bg.clientWidth) ? bg.clientWidth : window.innerWidth;
  const h = (bg && bg.clientHeight) ? bg.clientHeight : window.innerHeight;
  return { w: Math.max(320, w), h: Math.max(320, h) };
}

function bail() {
  document.body.classList.remove('gl-on');
  document.body.classList.add('no-webgl');
  if (canvas) canvas.style.display = 'none';
}

/* --- comprobación real de WebGL (no fiarse solo de la existencia del objeto) --- */
function webglOK() {
  try {
    const c = document.createElement('canvas');
    return !!(window.WebGLRenderingContext &&
      (c.getContext('webgl2') || c.getContext('webgl') || c.getContext('experimental-webgl')));
  } catch (e) { return false; }
}

let renderer, scene, camera, composer, clock, points, knot, raf = null, running = true;
const mouse = { x: 0, y: 0, tx: 0, ty: 0 };

function init() {
  if (!canvas || !webglOK()) { bail(); return; }

  try {
    renderer = new THREE.WebGLRenderer({
      canvas: canvas, alpha: true, antialias: !MOBILE, powerPreference: 'high-performance'
    });
  } catch (e) { bail(); return; }

  const dpr = Math.min(window.devicePixelRatio || 1, MOBILE ? 1.75 : 2);
  const box = heroBox();
  renderer.setPixelRatio(dpr);
  renderer.setSize(box.w, box.h);
  renderer.toneMapping = THREE.NoToneMapping;   // el OutputPass ya gestiona el color

  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(48, box.w / box.h, 0.1, 100);
  camera.position.set(0, 0, 7);
  clock = new THREE.Clock();

  /* ---------- partículas ---------- */
  const COUNT = MOBILE ? 420 : 1500;
  const pos = new Float32Array(COUNT * 3);
  const col = new Float32Array(COUNT * 3);
  const siz = new Float32Array(COUNT);
  const pha = new Float32Array(COUNT);
  const cGold = new THREE.Color('#e8c9a0');
  const cRose = new THREE.Color('#c9788a');
  const cBlush = new THREE.Color('#f6e3de');
  const tmp = new THREE.Color();

  for (let i = 0; i < COUNT; i++) {
    pos[i * 3] = (Math.random() - 0.5) * 16;
    pos[i * 3 + 1] = (Math.random() - 0.5) * 11;
    pos[i * 3 + 2] = (Math.random() - 0.5) * 8 - 1;
    const r = Math.random();
    tmp.copy(r < 0.52 ? cGold : (r < 0.86 ? cRose : cBlush));
    col[i * 3] = tmp.r; col[i * 3 + 1] = tmp.g; col[i * 3 + 2] = tmp.b;
    siz[i] = 0.5 + Math.random() * 2.1;
    pha[i] = Math.random() * Math.PI * 2;
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setAttribute('aColor', new THREE.BufferAttribute(col, 3));
  g.setAttribute('aSize', new THREE.BufferAttribute(siz, 1));
  g.setAttribute('aPhase', new THREE.BufferAttribute(pha, 1));

  const pm = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    uniforms: { uTime: { value: 0 }, uDpr: { value: dpr }, uFade: { value: 1 } },
    vertexShader: `
      attribute vec3 aColor; attribute float aSize; attribute float aPhase;
      uniform float uTime; uniform float uDpr; uniform float uFade;
      varying vec3 vColor; varying float vAlpha;
      void main(){
        vec3 p = position;
        p.y += sin(uTime * 0.22 + aPhase) * 0.32;
        p.x += cos(uTime * 0.17 + aPhase * 1.4) * 0.26;
        vec4 mv = modelViewMatrix * vec4(p, 1.0);
        gl_Position = projectionMatrix * mv;
        gl_PointSize = aSize * uDpr * (7.0 / -mv.z);
        vColor = aColor;
        vAlpha = (0.3 + 0.7 * abs(sin(uTime * 0.45 + aPhase))) * uFade;
      }`,
    fragmentShader: `
      varying vec3 vColor; varying float vAlpha;
      void main(){
        float d = length(gl_PointCoord - vec2(0.5));
        float a = smoothstep(0.5, 0.0, d);
        gl_FragColor = vec4(vColor, a * vAlpha);
      }`
  });
  points = new THREE.Points(g, pm);
  scene.add(points);

  /* ---------- nudo satinado (guino a la laca de unas) ---------- */
  const km = new THREE.ShaderMaterial({
    side: THREE.DoubleSide,
    uniforms: { uTime: { value: 0 } },
    vertexShader: `
      varying vec3 vN; varying vec3 vV; varying vec3 vP;
      void main(){
        vN = normalize(normalMatrix * normal);
        vec4 mv = modelViewMatrix * vec4(position, 1.0);
        vV = normalize(-mv.xyz);
        vP = position;
        gl_Position = projectionMatrix * mv;
      }`,
    fragmentShader: `
      uniform float uTime;
      varying vec3 vN; varying vec3 vV; varying vec3 vP;
      void main(){
        float f = pow(1.0 - max(dot(vN, vV), 0.0), 2.5);
        float grad = smoothstep(-1.3, 1.3, vP.y);
        vec3 gold = vec3(0.97, 0.82, 0.60);
        vec3 rose = vec3(0.84, 0.44, 0.55);
        vec3 deep = vec3(0.20, 0.07, 0.13);
        vec3 base = mix(deep, mix(rose, gold, grad), 0.78);
        vec3 col = base + gold * f * 0.72;
        vec3 ldir = normalize(vec3(sin(uTime * 0.3), 0.65, cos(uTime * 0.3)));
        float spec = pow(max(dot(vN, ldir), 0.0), 26.0);
        col += vec3(1.0) * spec * 0.32;
        gl_FragColor = vec4(col, 1.0);
      }`
  });
  knot = new THREE.Mesh(new THREE.TorusKnotGeometry(1.04, 0.30, MOBILE ? 120 : 220, 28), km);
  knot.position.set(MOBILE ? 0 : 2.45, MOBILE ? -1.5 : -0.45, MOBILE ? -0.8 : -0.6);
  knot.scale.setScalar(MOBILE ? 0.45 : 0.6);
  scene.add(knot);

  /* ---------- postproceso: bloom ---------- */
  composer = new EffectComposer(renderer);
  composer.setPixelRatio(dpr);
  const cb = heroBox();
  composer.setSize(cb.w, cb.h);
  composer.addPass(new RenderPass(scene, camera));
  const bloom = new UnrealBloomPass(
    new THREE.Vector2(cb.w, cb.h),
    MOBILE ? 0.30 : 0.36, 0.8, 0.78
  );
  composer.addPass(bloom);
  composer.addPass(new OutputPass());

  document.body.classList.add('gl-on');

  /* ---------- eventos ---------- */
  window.addEventListener('resize', onResize);
  window.addEventListener('pointermove', function (e) {
    mouse.tx = (e.clientX / window.innerWidth - 0.5) * 2;
    mouse.ty = (e.clientY / window.innerHeight - 0.5) * 2;
  }, { passive: true });
  canvas.addEventListener('webglcontextlost', function (e) { e.preventDefault(); bail(); });
  document.addEventListener('visibilitychange', function () {
    running = !document.hidden;
    if (running && !reduce) loop();
  });

  if (reduce) { render(0); return; }   // sin animacion: un solo fotograma
  loop();
}

function onResize() {
  if (!renderer) return;
  const hb = heroBox();
  const w = hb.w, h = hb.h;
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h);
  if (composer) composer.setSize(w, h);
  if (knot) {
    const m = w < 820;
    knot.position.set(m ? 0 : 2.45, m ? -1.5 : -0.45, m ? -0.8 : -0.6);
    knot.scale.setScalar(m ? 0.45 : 0.6);
  }
}

function render(t) {
  const sy = window.scrollY || window.pageYOffset || 0;
  const fade = Math.max(0, 1 - sy / (window.innerHeight * 0.9));   // se desvanece al bajar
  if (points) {
    points.material.uniforms.uTime.value = t;
    points.material.uniforms.uFade.value = fade;
  }
  if (knot) {
    knot.material.uniforms.uTime.value = t;
    knot.rotation.y = t * 0.16 + mouse.x * 0.25;
    knot.rotation.x = Math.sin(t * 0.22) * 0.18 + mouse.y * 0.16;
    knot.visible = fade > 0.02;
    knot.scale.setScalar((window.innerWidth < 820 ? 0.45 : 0.6) * (0.85 + fade * 0.15));
  }
  mouse.x += (mouse.tx - mouse.x) * 0.045;
  mouse.y += (mouse.ty - mouse.y) * 0.045;
  if (camera) {
    camera.position.x = mouse.x * 0.28;
    camera.position.y = -mouse.y * 0.20;
    camera.lookAt(0, 0, 0);
  }
  if (composer) composer.render();
}

function loop() {
  if (raf) cancelAnimationFrame(raf);
  const tick = function () {
    raf = requestAnimationFrame(tick);
    if (!running) return;
    const sy = window.scrollY || 0;
    if (sy > window.innerHeight * 1.6) return;    // fuera de vista: no gastamos GPU
    render(clock.getElapsedTime());
  };
  raf = requestAnimationFrame(tick);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
