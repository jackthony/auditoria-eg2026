/* ═══════════ SITE-NAV · inyecta header + footer en 9 páginas ═══════════ */
(function () {
  'use strict';

  // Raíz absoluta del sitio (soporta gh-pages y local)
  const ROOT = (function () {
    const p = location.pathname;
    // /foo/bar/ → devuelve hasta raíz: "" para domain root, o subpath
    // auditoria.neuracode.dev/ → root = ""
    // 127.0.0.1:8765/ → root = ""
    return '';
  })();

  const CASES = [
    { slug: '/',                 t: 'Dashboard técnico',       p: 'Monitor SHA-256 + hallazgos' },
    { slug: '/chat/',            t: 'Tía María pregunta',      p: 'Sin jerga, solo lo esencial' },
    { slug: '/historia/',        t: 'Historia editorial',      p: 'Narrativa mesa a mesa' },
    { slug: '/impugnadas/',      t: 'Impugnadas Lima+Exterior',p: 'z=3.9 sobre rural' },
    { slug: '/mesas-faltantes/', t: 'Mesas faltantes',         p: '4,703 sin acta publicada' },
    { slug: '/mesas-lentas/',    t: 'Mesas lentas',            p: 'Retraso anómalo de escrutinio' },
    { slug: '/ranking-cambia/',  t: 'Ranking cambia',          p: '2° puesto cambia al sumar' },
    { slug: '/fdr/',             t: 'FDR (falsos descubrimientos)', p: 'Corrección Benjamini-Hochberg' },
  ];

  const SOCIAL = [
    { href: 'https://github.com/jackthony/auditoria-eg2026', t: 'GitHub' },
    { href: 'https://www.linkedin.com/in/jackaguilarc/',     t: 'LinkedIn' },
    { href: 'https://x.com/JackTonyAC',                      t: 'X' },
    { href: 'https://www.tiktok.com/@jack.de.neura.code',    t: 'TikTok' },
    { href: 'https://www.instagram.com/neuracode.dev/',      t: 'IG Neuracode' },
    { href: 'https://www.instagram.com/jackdeneuracode/',    t: 'IG Jack' },
    { href: 'https://www.facebook.com/neuracode/',           t: 'FB Neuracode' },
    { href: 'https://www.neuracode.dev/comunidad',           t: 'Neuracode Academy' },
  ];

  const current = location.pathname.replace(/index\.html$/, '').replace(/\/+$/, '/') || '/';

  // ═════ HEADER ═════
  function buildHeader() {
    const logo = ROOT + '/logo-neuracode-tight.png';
    const items = CASES.map(c => {
      const active = (c.slug === current) ? ' sn-active' : '';
      return `<a class="sn-case${active}" href="${c.slug}">
        <div class="sn-t">${c.t}</div>
        <div class="sn-p">${c.p}</div>
      </a>`;
    }).join('');

    const header = document.createElement('header');
    header.className = 'site-header';
    header.innerHTML = `
      <div class="sn-bar">
        <a href="/" class="sn-brand" aria-label="Inicio auditoría EG2026">
          <img src="${logo}" alt="Neuracode" onerror="this.style.display='none'">
          <span>
            <span class="sn-wordmark">Neuracode<span class="sn-dot">.</span>Auditoría</span>
            <span class="sn-sub">EG2026 · Perú</span>
          </span>
        </a>
        <div class="sn-spacer"></div>
        <div class="sn-cases">
          <button class="sn-btn" id="sn-btn" aria-haspopup="true" aria-expanded="false">
            Casos <span class="sn-caret">▼</span>
          </button>
          <div class="sn-dropdown" id="sn-dropdown" role="menu">${items}</div>
        </div>
      </div>
    `;
    return header;
  }

  // ═════ FOOTER ═════
  function buildFooter() {
    const logo = ROOT + '/logo-neuracode-tight.png';
    const social = SOCIAL.map(s =>
      `<a href="${s.href}" target="_blank" rel="noopener">${s.t}</a>`
    ).join('');

    const footer = document.createElement('footer');
    footer.className = 'site-footer';
    footer.innerHTML = `
      <div class="sn-fbar">
        <div class="sn-fbrand">
          <img src="${logo}" alt="Neuracode">
          <span class="sn-wordmark">Neuracode<span class="sn-dot">.</span>Auditoría</span>
        </div>
        <div class="sn-fbody">
          Auditoría ciudadana EG2026 · Por <strong>Jack Aguilar</strong> · Sin afiliación política.
          <div class="sn-social">${social}</div>
          <div class="sn-meta" id="sn-sha">SHA-256: calculando…</div>
          <div class="sn-license">Licencia MIT (código) · CC-BY-4.0 (datos) · Datos públicos ONPE.</div>
        </div>
      </div>
    `;
    return footer;
  }

  // ═════ WIRE UP ═════
  function init() {
    // Injector: si la página trae su propio header/footer, se respeta; si no, se prepone/apende.
    if (!document.querySelector('.site-header')) {
      document.body.insertBefore(buildHeader(), document.body.firstChild);
    }
    if (!document.querySelector('.site-footer')) {
      document.body.appendChild(buildFooter());
    }

    // Dropdown toggle
    const btn = document.getElementById('sn-btn');
    const dd  = document.getElementById('sn-dropdown');
    if (btn && dd) {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const open = dd.classList.toggle('sn-open');
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
      document.addEventListener('click', () => {
        dd.classList.remove('sn-open');
        btn.setAttribute('aria-expanded', 'false');
      });
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') dd.classList.remove('sn-open');
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
