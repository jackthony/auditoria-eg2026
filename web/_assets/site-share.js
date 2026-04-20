/* ═══════════ SITE-SHARE · FAB unificado ═══════════ */
/* Lee meta tags de la propia página (og:*, twitter:*) para auto-presets DRY */

(function () {
  'use strict';

  const HASHTAGS = 'EG2026,ONPE,Auditoria';

  const meta = (name) => {
    const el = document.querySelector(
      `meta[property="${name}"], meta[name="${name}"]`
    );
    return el ? el.getAttribute('content') : null;
  };

  const getShareData = () => {
    const title = meta('og:title') || document.title;
    const text  = meta('twitter:description') || meta('og:description') || meta('description') || title;
    const canonical = document.querySelector('link[rel="canonical"]');
    const url = (canonical && canonical.href) || meta('og:url') || location.href;
    return { title, text, url };
  };

  const buildFab = () => {
    const fab = document.createElement('button');
    fab.className = 'ss-fab';
    fab.setAttribute('aria-label', 'Compartir esta página');
    fab.setAttribute('aria-haspopup', 'menu');
    fab.innerHTML = `
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92s2.92-1.31 2.92-2.92-1.31-2.92-2.92-2.92z"/></svg>
    `;
    return fab;
  };

  const buildMenu = () => {
    const menu = document.createElement('div');
    menu.className = 'ss-menu';
    menu.setAttribute('role', 'menu');
    menu.innerHTML = `
      <div class="ss-title">Compartir</div>
      <a href="#" data-ch="x"    role="menuitem"><span class="ss-ic ss-ic-x">𝕏</span> X (Twitter)</a>
      <a href="#" data-ch="fb"   role="menuitem"><span class="ss-ic ss-ic-fb">f</span> Facebook</a>
      <a href="#" data-ch="wa"   role="menuitem"><span class="ss-ic ss-ic-wa">W</span> WhatsApp</a>
      <a href="#" data-ch="tg"   role="menuitem"><span class="ss-ic ss-ic-tg">T</span> Telegram</a>
      <a href="#" data-ch="li"   role="menuitem"><span class="ss-ic ss-ic-li">in</span> LinkedIn</a>
      <a href="#" data-ch="copy" role="menuitem"><span class="ss-ic ss-ic-co">@</span> Copiar link</a>
    `;
    return menu;
  };

  const toast = (msg) => {
    let el = document.querySelector('.ss-toast');
    if (!el) {
      el = document.createElement('div');
      el.className = 'ss-toast';
      document.body.appendChild(el);
    }
    el.textContent = msg;
    requestAnimationFrame(() => el.classList.add('ss-show'));
    setTimeout(() => el.classList.remove('ss-show'), 1800);
  };

  const targetFor = (ch, data) => {
    const enc = encodeURIComponent;
    const { text, url } = data;
    switch (ch) {
      case 'x':  return `https://twitter.com/intent/tweet?text=${enc(text)}&url=${enc(url)}&hashtags=${enc(HASHTAGS)}`;
      case 'fb': return `https://www.facebook.com/sharer/sharer.php?u=${enc(url)}`;
      case 'wa': return `https://api.whatsapp.com/send?text=${enc(text + ' · ' + url)}`;
      case 'tg': return `https://t.me/share/url?url=${enc(url)}&text=${enc(text)}`;
      case 'li': return `https://www.linkedin.com/sharing/share-offsite/?url=${enc(url)}`;
      default:   return null;
    }
  };

  const init = () => {
    // Evita duplicar si ya existe un FAB propio en la página (ej. chat/, historia/)
    if (document.querySelector('.ss-fab, .share-fab')) return;

    const fab  = buildFab();
    const menu = buildMenu();
    document.body.appendChild(fab);
    document.body.appendChild(menu);

    fab.addEventListener('click', (e) => {
      e.stopPropagation();
      // Si el navegador soporta Web Share API (móviles, Safari) → sheet nativo
      if (navigator.share && /Android|iPhone|iPad/i.test(navigator.userAgent)) {
        navigator.share(getShareData()).catch(() => menu.classList.toggle('ss-open'));
        return;
      }
      menu.classList.toggle('ss-open');
    });

    document.addEventListener('click', () => menu.classList.remove('ss-open'));
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') menu.classList.remove('ss-open');
    });

    menu.querySelectorAll('a[data-ch]').forEach(a => {
      a.addEventListener('click', async (e) => {
        e.preventDefault();
        const ch = a.dataset.ch;
        const data = getShareData();
        if (ch === 'copy') {
          try {
            await navigator.clipboard.writeText(data.url);
            toast('Link copiado');
          } catch {
            toast('No se pudo copiar');
          }
          menu.classList.remove('ss-open');
          return;
        }
        const t = targetFor(ch, data);
        if (t) window.open(t, '_blank', 'noopener,noreferrer,width=640,height=540');
        menu.classList.remove('ss-open');
      });
    });
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
