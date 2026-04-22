import { test, expect, Page } from '@playwright/test';
import * as path from 'path';

const WEB_ROOT = 'C:/Users/jaaguilar/Documents/elecciones2026/auditoria-eg2026/web';
const URLS = [
  { slug: 'h1', url: `file:///${WEB_ROOT}/h1/index.html` },
  { slug: 'h4', url: `file:///${WEB_ROOT}/h4/index.html` },
  { slug: 'h9', url: `file:///${WEB_ROOT}/h9/index.html` },
  { slug: 'h12', url: `file:///${WEB_ROOT}/h12/index.html` },
];

const DESKTOP = { width: 1440, height: 900 };
const MOBILE = { width: 390, height: 844 };

const OUT_DIR = 'C:/Users/jaaguilar/Documents/elecciones2026/auditoria-eg2026/reports/qa_visual_20260420';

const FORBIDDEN_STRINGS = ['Regla de oro', 'jamás "fraude"'];

async function checkOverlap(page: Page): Promise<{
  headerBottom: number;
  toggleTop: number;
  gap: number;
  overlap: boolean;
  error?: string;
}> {
  await page.evaluate(() => window.scrollTo(0, 500));
  await page.waitForTimeout(400);

  return page.evaluate(() => {
    const header = document.querySelector('.site-header');
    const toggle = document.querySelector('.voice-toggle-wrap');
    if (!header || !toggle) {
      return {
        headerBottom: -1,
        toggleTop: -1,
        gap: -1,
        overlap: false,
        error: `missing: header=${!!header} toggle=${!!toggle}`,
      };
    }
    const hRect = header.getBoundingClientRect();
    const tRect = toggle.getBoundingClientRect();
    return {
      headerBottom: Math.round(hRect.bottom),
      toggleTop: Math.round(tRect.top),
      gap: Math.round(tRect.top - hRect.bottom),
      overlap: tRect.top < hRect.bottom,
    };
  });
}

async function checkLeaks(page: Page): Promise<string[]> {
  const content = await page.content();
  return FORBIDDEN_STRINGS.filter(s => content.includes(s));
}

async function checkVoiceToggle(page: Page): Promise<{
  techResult: boolean;
  popResult: boolean;
  buttonCount: number;
  error?: string;
}> {
  await page.evaluate(() => document.body.removeAttribute('data-voice'));

  const allButtons = page.locator('.voice-toggle-wrap button, .voice-toggle button');
  const count = await allButtons.count();

  if (count === 0) {
    const toggleExists = (await page.locator('.voice-toggle-wrap, .voice-toggle, [data-voice]').count()) > 0;
    return { techResult: false, popResult: false, buttonCount: 0, error: `no buttons found, toggleExists=${toggleExists}` };
  }

  let techResult = false;
  let popResult = false;

  // Try to find and click tech button
  for (let i = 0; i < count; i++) {
    const btn = allButtons.nth(i);
    const text = ((await btn.textContent()) ?? '').toLowerCase();
    if (text.includes('técnico') || text.includes('tecnico') || text.includes('tech')) {
      await btn.click();
      const attr = await page.evaluate(() => document.body.getAttribute('data-voice'));
      techResult = attr === 'tech';
      break;
    }
  }

  // Try to find and click pop button
  for (let i = 0; i < count; i++) {
    const btn = allButtons.nth(i);
    const text = ((await btn.textContent()) ?? '').toLowerCase();
    if (text.includes('pueblo') || text.includes('pop') || text.includes('ciudadan')) {
      await btn.click();
      const attr = await page.evaluate(() => document.body.getAttribute('data-voice'));
      popResult = attr === 'pop';
      break;
    }
  }

  // If no labeled buttons, try cycling
  if (!techResult && !popResult && count >= 1) {
    await allButtons.first().click();
    const attr1 = await page.evaluate(() => document.body.getAttribute('data-voice'));
    techResult = attr1 !== null;
    await allButtons.first().click();
    const attr2 = await page.evaluate(() => document.body.getAttribute('data-voice'));
    popResult = attr2 !== attr1;
  }

  return { techResult, popResult, buttonCount: count };
}

for (const { slug, url } of URLS) {
  test(`[${slug}] desktop`, async ({ page }) => {
    await page.setViewportSize(DESKTOP);
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 15000 });

    // Check 1: Overlap after scroll
    const overlap = await checkOverlap(page);
    console.log(`[${slug}][desktop] overlap:`, JSON.stringify(overlap));

    // Check 2: Leak
    const leaks = await checkLeaks(page);
    console.log(`[${slug}][desktop] leaks:`, leaks.length === 0 ? 'NONE' : leaks);

    // Check 3: Voice toggle
    await page.reload({ waitUntil: 'domcontentloaded' });
    const toggle = await checkVoiceToggle(page);
    console.log(`[${slug}][desktop] toggle:`, JSON.stringify(toggle));

    // Screenshot post-scroll
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.evaluate(() => window.scrollTo(0, 500));
    await page.waitForTimeout(400);
    const ssPath = path.join(OUT_DIR, `${slug}_desktop.png`);
    await page.screenshot({ path: ssPath });
    console.log(`[${slug}][desktop] screenshot: ${ssPath}`);

    // Assertions
    expect(leaks, `[${slug}] desktop: forbidden strings found`).toHaveLength(0);
    if (!overlap.error) {
      expect(overlap.overlap, `[${slug}] desktop: voice-toggle overlaps header (gap=${overlap.gap}px)`).toBe(false);
    }
  });

  test(`[${slug}] mobile`, async ({ page }) => {
    await page.setViewportSize(MOBILE);
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 15000 });

    // Check 1: Overlap after scroll
    const overlap = await checkOverlap(page);
    console.log(`[${slug}][mobile] overlap:`, JSON.stringify(overlap));

    // Check 2: Leak
    const leaks = await checkLeaks(page);
    console.log(`[${slug}][mobile] leaks:`, leaks.length === 0 ? 'NONE' : leaks);

    // Check 3: Voice toggle
    await page.reload({ waitUntil: 'domcontentloaded' });
    const toggle = await checkVoiceToggle(page);
    console.log(`[${slug}][mobile] toggle:`, JSON.stringify(toggle));

    // Screenshot post-scroll
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.evaluate(() => window.scrollTo(0, 500));
    await page.waitForTimeout(400);
    const ssPath = path.join(OUT_DIR, `${slug}_mobile.png`);
    await page.screenshot({ path: ssPath });
    console.log(`[${slug}][mobile] screenshot: ${ssPath}`);

    // Assertions
    expect(leaks, `[${slug}] mobile: forbidden strings found`).toHaveLength(0);
    if (!overlap.error) {
      expect(overlap.overlap, `[${slug}] mobile: voice-toggle overlaps header (gap=${overlap.gap}px)`).toBe(false);
    }
  });
}
