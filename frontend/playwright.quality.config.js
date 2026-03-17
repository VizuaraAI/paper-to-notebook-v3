import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './tests',
  testMatch: 'quality.spec.js',
  use: {
    baseURL: 'http://localhost:5173',
  },
})
