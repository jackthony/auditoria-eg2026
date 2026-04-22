import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: '.',
  testMatch: '**/*.spec.ts',
  timeout: 60000,
  retries: 1,
  use: {
    headless: true,
    locale: 'es-PE',
    launchOptions: {
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security', '--allow-file-access-from-files'],
    },
  },
  reporter: [
    ['list'],
    ['json', { outputFile: 'C:/Users/jaaguilar/Documents/elecciones2026/auditoria-eg2026/reports/qa_visual_20260420/results.json' }],
  ],
});
