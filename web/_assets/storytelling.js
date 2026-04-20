/* ═══════════ STORYTELLING · helpers narrativos ═══════════ */
/* Activadores automáticos para elementos dentro de <div class="storytelling">.
   Cada helper respeta prefers-reduced-motion (muestra estado final).

   Uso:
     <div class="storytelling">
       <section class="scene" data-scene="1">...</section>
       <div class="counter" data-counter-to="88063" data-counter-dur="2200">0</div>
       <div class="dots-grid" data-dots-total="800" data-dots-off="43"></div>
       <div class="rank-row" data-rank-delay="0">...</div>
     </div>
*/

(function () {
  'use strict';

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Mulberry32 PRNG — determinista (credibilidad forense: periodista graba 2 videos = misma distribución).
  function mulberry32(a) {
    return function () {
      a |= 0; a = a + 0x6D2B79F5 | 0;
      let t = a;
      t = Math.imul(t ^ t >>> 15, t | 1);
      t ^= t + Math.imul(t ^ t >>> 7, t | 61);
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }

  // ═════ IntersectionObserver · fade-in scenes + trigger helpers ═════
  function initScenes(root) {
    const scenes = root.querySelectorAll('.scene');
    if (!scenes.length) return;

    if (reduced) {
      scenes.forEach(s => s.classList.add('in'));
      scenes.forEach(runSceneEffects);
      return;
    }

    const io = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add('in');
          runSceneEffects(e.target);
        }
      });
    }, { threshold: 0.3 });

    scenes.forEach(s => io.observe(s));
  }

  function runSceneEffects(scene) {
    scene.querySelectorAll('.counter[data-counter-to]').forEach(animateCounter);
    scene.querySelectorAll('.dots-grid[data-dots-total]').forEach(animateDots);
    scene.querySelectorAll('.rank-row').forEach(animateRank);
  }

  // ═════ COUNTER · 0 → N ═════
  function animateCounter(el) {
    if (el.dataset.done) return;
    el.dataset.done = '1';
    const target = parseInt(el.dataset.counterTo, 10) || 0;
    const dur = parseInt(el.dataset.counterDur, 10) || 2200;
    const locale = el.dataset.counterLocale || 'es-PE';
    if (reduced) { el.textContent = target.toLocaleString(locale); return; }
    const t0 = performance.now();
    function step(t) {
      const p = Math.min(1, (t - t0) / dur);
      const ease = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.floor(target * ease).toLocaleString(locale);
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  // ═════ DOTS GRID · N dots, M rojos aleatorios ═════
  function animateDots(g) {
    if (g.dataset.done) return;
    g.dataset.done = '1';
    const TOTAL = parseInt(g.dataset.dotsTotal, 10) || 800;
    const OFF   = parseInt(g.dataset.dotsOff, 10) || Math.round(TOTAL * 0.05);
    const seed  = parseInt(g.dataset.dotsSeed, 10) || 42;
    const rand  = mulberry32(seed);
    const offIdx = new Set();
    while (offIdx.size < OFF) offIdx.add(Math.floor(rand() * TOTAL));

    for (let i = 0; i < TOTAL; i++) {
      const d = document.createElement('div');
      d.className = 'dot';
      g.appendChild(d);
    }

    if (reduced) {
      [...g.children].forEach((d, i) => {
        if (offIdx.has(i)) d.classList.add('off');
      });
      return;
    }

    // Reveal con delay escalonado
    let i = 0;
    const children = [...g.children];
    const per = Math.max(1, Math.floor(1400 / TOTAL));
    function reveal() {
      if (i >= TOTAL) return;
      if (offIdx.has(i)) children[i].classList.add('off');
      i++;
      setTimeout(reveal, per);
    }
    reveal();
  }

  // ═════ RANK ROW · cascade left-to-right ═════
  function animateRank(row) {
    if (row.dataset.done) return;
    row.dataset.done = '1';
    const delay = parseInt(row.dataset.rankDelay, 10) || 0;
    if (reduced) { row.classList.add('in'); return; }
    setTimeout(() => row.classList.add('in'), delay);
  }

  // ═════ HANDWRITE fade-in (opcional por data attr) ═════
  function initHandwrites(root) {
    const items = root.querySelectorAll('.handwrite[data-fade]');
    if (!items.length || reduced) {
      items.forEach(el => { el.style.opacity = 1; });
      return;
    }
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.style.transition = 'opacity 1.4s ease';
          e.target.style.opacity = '1';
        }
      });
    }, { threshold: 0.5 });
    items.forEach(el => { el.style.opacity = '0'; io.observe(el); });
  }

  // ═════ WIRE UP ═════
  function init() {
    const roots = document.querySelectorAll('.storytelling');
    if (!roots.length) return;
    roots.forEach(r => {
      initScenes(r);
      initHandwrites(r);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
