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
    { slug: '/',     t: 'Inicio',                   p: 'Landing · hallazgos principales' },
    { slug: '/h4/',  t: 'H4 · JPP 41% mesas 900k+', p: 'Hallazgo crítico · voto especial' },
    { slug: null,    t: 'Roadmap · H1/H2/H9/H12',   p: 'Pronto', wip: true },
  ];

  const SOCIAL_GROUPS = [
    {
      label: 'Jack',
      items: [
        { href: 'https://www.linkedin.com/in/jackaguilarc/',  t: 'LinkedIn' },
        { href: 'https://x.com/JackTonyAC',                   t: 'X' },
        { href: 'https://www.tiktok.com/@jack.de.neura.code', t: 'TikTok' },
        { href: 'https://www.instagram.com/jackdeneuracode/', t: 'IG' },
        { href: 'https://www.instagram.com/jacktonyac/',      t: 'IG personal' },
        { href: 'https://www.facebook.com/jack.tony.1804',    t: 'FB' },
      ],
    },
    {
      label: 'Neuracode',
      items: [
        { href: 'https://www.instagram.com/neuracode.dev/',      t: 'IG' },
        { href: 'https://www.facebook.com/neuracode/',           t: 'FB' },
        { href: 'https://www.neuracode.dev/comunidad',           t: 'Academy' },
        { href: 'https://github.com/jackthony/auditoria-eg2026', t: 'GitHub' },
      ],
    },
  ];

  const current = location.pathname.replace(/index\.html$/, '').replace(/\/+$/, '/') || '/';

  // ═════ HEADER ═════
  function buildHeader() {
    const logo = ROOT + '/logo-neuracode-tight.png';
    const items = CASES.map(c => {
      const active = (c.slug && c.slug === current) ? ' sn-active' : '';
      const wip = c.wip ? ' sn-wip' : '';
      const tag = c.slug ? 'a' : 'span';
      const href = c.slug ? ` href="${c.slug}"` : '';
      const role = c.slug ? '' : ' aria-disabled="true"';
      return `<${tag} class="sn-case${active}${wip}"${href}${role}>
        <div class="sn-t">${c.t}</div>
        <div class="sn-p">${c.p}</div>
      </${tag}>`;
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

  // ═════ SOCIAL · render reutilizable en 3 columnas ═════
  function renderSocialGroups() {
    return SOCIAL_GROUPS.map(g => {
      const links = g.items.map(s =>
        `<a href="${s.href}" target="_blank" rel="noopener">${s.t}</a>`
      ).join('');
      return `
        <div class="sn-ss-col">
          <div class="sn-ss-label">${g.label}</div>
          <div class="sn-ss-links">${links}</div>
        </div>
      `;
    }).join('');
  }

  // ═════ FOOTER ═════
  function buildFooter() {
    const logo = ROOT + '/logo-neuracode-tight.png';
    const footer = document.createElement('footer');
    footer.className = 'site-footer';
    footer.innerHTML = `
      <div class="sn-fbar">
        <div class="sn-fbrand">
          <img src="${logo}" alt="Neuracode">
          <span class="sn-wordmark">Neuracode<span class="sn-dot">.</span>Auditoría</span>
        </div>
        <div class="sn-fbody">
          Autoría: <strong>Jack Aguilar</strong>. Análisis técnico reproducible. Cualquiera verifica.
          <div class="sn-social-grid">${renderSocialGroups()}</div>
          <div class="sn-meta" id="sn-sha">SHA-256: calculando…</div>
          <div class="sn-license">Licencia MIT (código) · CC-BY-4.0 (datos) · Datos públicos ONPE.</div>
        </div>
      </div>
    `;
    return footer;
  }

  // ═════ STRIP SOCIAL · para footers preexistentes ═════
  function buildSocialStrip() {
    const strip = document.createElement('div');
    strip.className = 'sn-social-strip';
    strip.innerHTML = `<div class="sn-social-grid">${renderSocialGroups()}</div>`;
    return strip;
  }

  // ═════ CASES MARKUP · reutilizable para float + mount ═════
  function buildCasesMarkup() {
    const items = CASES.map(c => {
      const active = (c.slug && c.slug === current) ? ' sn-active' : '';
      const wip = c.wip ? ' sn-wip' : '';
      const tag = c.slug ? 'a' : 'span';
      const href = c.slug ? ` href="${c.slug}"` : '';
      const role = c.slug ? '' : ' aria-disabled="true"';
      return `<${tag} class="sn-case${active}${wip}"${href}${role}>
        <div class="sn-t">${c.t}</div>
        <div class="sn-p">${c.p}</div>
      </${tag}>`;
    }).join('');
    return `
      <button class="sn-btn" id="sn-btn" aria-haspopup="true" aria-expanded="false" aria-label="Menú de casos">
        Casos <span class="sn-caret">▼</span>
      </button>
      <div class="sn-dropdown" id="sn-dropdown" role="menu">${items}</div>
    `;
  }

  // ═════ FLOATING CASES · fallback para header propio sin .sn-mount ═════
  function buildFloatingCases() {
    const wrap = document.createElement('div');
    wrap.className = 'sn-float sn-cases';
    wrap.innerHTML = buildCasesMarkup();
    return wrap;
  }

  // ═════ MOUNTED CASES · ancla dentro de <.sn-mount> del header propio ═════
  function mountCasesInto(target) {
    target.classList.add('sn-cases');
    target.innerHTML = buildCasesMarkup();
  }

  // ═════ SELLO EG2026 · franja roja top (signature visual) ═════
  function buildSello() {
    const sello = document.createElement('div');
    sello.className = 'sn-sello';
    sello.setAttribute('aria-hidden', 'true');
    return sello;
  }

  // ═════ SKIP-TO-CONTENT · WCAG 2.4.1 ═════
  function buildSkipLink() {
    const skip = document.createElement('a');
    skip.className = 'sn-skip';
    skip.href = '#sn-main';
    skip.textContent = 'Saltar al contenido';
    return skip;
  }

  // Inserta ancla #sn-main en el primer <section>/<article>/<main> tras el header.
  function ensureMainAnchor() {
    if (document.getElementById('sn-main')) return;
    const target =
      document.querySelector('main') ||
      document.querySelector('header ~ section, header ~ article, header ~ div.phone-outer, header ~ .scene');
    if (target) {
      target.id = target.id || 'sn-main';
      if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
    }
  }

  // ═════ WIRE UP ═════
  function init() {
    // Sello rojo primero (siempre al top absoluto)
    if (!document.querySelector('.sn-sello')) {
      document.body.insertBefore(buildSello(), document.body.firstChild);
    }
    // Skip link para teclado
    if (!document.querySelector('.sn-skip')) {
      document.body.insertBefore(buildSkipLink(), document.body.firstChild);
    }
    ensureMainAnchor();
    // Regla:
    //  - Si la página NO tiene ningún <header> (ni propio ni .site-header) → inyectar header completo.
    //  - Si tiene header propio → inyectar solo botón flotante "Casos".
    //  - Nunca duplicar headers.
    const hasAnyHeader = document.querySelector('header, .site-header');
    const mountPoint = document.querySelector('.sn-mount');
    if (!hasAnyHeader) {
      document.body.insertBefore(buildHeader(), document.querySelector('.sn-sello').nextSibling);
    } else if (mountPoint) {
      mountCasesInto(mountPoint);
    } else if (!document.querySelector('.sn-float')) {
      document.body.appendChild(buildFloatingCases());
    }
    const existingFooter = document.querySelector('footer, .site-footer');
    if (!existingFooter) {
      // Sin footer propio → inyectar completo
      document.body.appendChild(buildFooter());
    } else if (!existingFooter.querySelector('.sn-social-strip')) {
      // Con footer propio → anexar solo el strip social
      existingFooter.appendChild(buildSocialStrip());
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
