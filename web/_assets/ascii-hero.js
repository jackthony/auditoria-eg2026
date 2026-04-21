/* ═══════════ ASCII HERO · renderer vanilla ═══════════ */
/* Requiere <pre id="ah-art"> dentro de .ascii-hero. */
/* Datos: HALL-0420-H4 (92,766 mesas · JPP 10.91% normales vs 41.65% en 900k+). */

(function () {
  'use strict';

  const NORMAL_PCT = 10.91;
  const ALERT_PCT  = 41.65;
  const GAP_PCT    = 30.74;

  const BAR  = " ▏▎▍▌▋▊▉█";
  const COLS = 78;
  const LABEL_W = 13;

  function renderBar(pct, maxPct) {
    const barW = COLS - LABEL_W - 10;
    const filled = Math.round((pct / maxPct) * barW * 8) / 8;
    const full = Math.floor(filled);
    const rem  = filled - full;
    const idx  = Math.round(rem * 8);
    const partial = idx > 0 ? BAR[idx] : "";
    const emptyW  = barW - full - (partial ? 1 : 0);
    return BAR[8].repeat(full) + partial + " ".repeat(Math.max(0, emptyW));
  }

  function frame(progress) {
    const p = Math.min(1, Math.max(0, progress));
    const ease = 1 - Math.pow(1 - p, 3);
    const nCur = NORMAL_PCT * ease;
    const aCur = ALERT_PCT  * ease;
    const gCur = GAP_PCT    * ease;
    const MAX  = 50;

    const title1 = "  ░░ ANOMALÍA ESTADÍSTICA · ONPE DEBE EXPLICAR ░░                             ";
    const barN = renderBar(nCur, MAX);
    const barA = renderBar(aCur, MAX);
    const barG = BAR[8].repeat(Math.round((gCur / 50) * (COLS - LABEL_W - 10)));
    const barGPad = barG.padEnd(COLS - LABEL_W - 10);

    const ratio = (aCur / Math.max(0.01, nCur)).toFixed(2);
    const tN = `${nCur.toFixed(2).padStart(5)}%`;
    const tA = `${aCur.toFixed(2).padStart(5)}%`;
    const tG = `${gCur.toFixed(2).padStart(5)}pp`;

    return [
      `<span class="ah-lab">${title1}</span>`,
      `<span class="ah-lab">                                                                              </span>`,
      `<span class="ah-lab">MESAS NORMAL </span><span class="ah-norm">${barN}</span><span class="ah-norm">  ${tN}</span>`,
      `<span class="ah-lab">MESAS 900k+  </span><span class="ah-alert">${barA}</span><span class="ah-alert">  ${tA}</span>`,
      `<span class="ah-lab">                                                                              </span>`,
      `<span class="ah-lab">BRECHA       </span><span class="ah-gap">${barGPad}</span><span class="ah-gap">  ${tG}</span>`,
      `<span class="ah-lab">                                                                              </span>`,
      `<span class="ah-meta">  ratio ${ratio}×   ·   4,703 mesas especiales   ·   88,063 normales         </span>`,
      `<span class="ah-meta">  código 900001–904703 · militar · exterior · penal · hospitalario            </span>`,
    ].join("\n");
  }

  function mount(el) {
    let startTs = null;
    let rafId = null;
    const DURATION = 2600;
    const HOLD = 1800;

    function tick(ts) {
      if (!startTs) startTs = ts;
      const e = ts - startTs;
      if (e < DURATION) {
        el.innerHTML = frame(e / DURATION);
        rafId = requestAnimationFrame(tick);
      } else if (e < DURATION + HOLD) {
        el.innerHTML = frame(1);
        rafId = requestAnimationFrame(tick);
      } else {
        startTs = ts;
        rafId = requestAnimationFrame(tick);
      }
    }

    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced) {
      el.innerHTML = frame(1);
      return;
    }
    rafId = requestAnimationFrame(tick);
  }

  function init() {
    document.querySelectorAll('.ascii-hero pre.ah-art').forEach(mount);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
