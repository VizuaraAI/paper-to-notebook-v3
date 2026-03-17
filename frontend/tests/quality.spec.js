/**
 * Quality E2E Test — Real Gemini API Call
 *
 * This test opens a VISIBLE browser, waits for you to type your Gemini API key,
 * then generates a real notebook from "Attention Is All You Need" and validates it.
 *
 * Run with:
 *   cd frontend && npx playwright test tests/quality.spec.js --headed
 *
 * Prerequisites:
 *   - Backend running: cd backend && ../venv/bin/python -m uvicorn main:app --port 8000
 *   - Frontend running: cd frontend && npm run dev
 */

import { test, expect } from '@playwright/test'
import { execSync } from 'child_process'
import fs from 'fs'
import path from 'path'

// This test uses real API calls — give it plenty of time
test.setTimeout(180_000) // 3 minutes

const ARXIV_URL = 'https://arxiv.org/abs/1706.03762'
const OUTPUT_DIR = path.join(import.meta.dirname, 'output')
const REQUIRED_SECTIONS = [
  /opening|introduction|paper\s*title|summary/i,
  /initialization|setup|install|import/i,
  /context|problem|background|motivation/i,
  /data|dataset|preparation/i,
  /evaluat|metric|loss|scoring/i,
  /baseline|reference|benchmark/i,
  /algorithm|implementation|method|attention/i,
  /conclus|summary|takeaway|result/i,
]

test('real E2E: generate notebook from Attention Is All You Need', async ({ page }) => {
  // Step 1: Navigate to the app
  await page.goto('/')
  await page.screenshot({ path: 'tests/screenshots/quality-01-initial.png' })

  // Step 2: Fill in the arXiv URL
  await page.getByTestId('arxiv-url-input').fill(ARXIV_URL)
  await page.screenshot({ path: 'tests/screenshots/quality-02-url-filled.png' })

  // Step 3: Wait for user to type their API key (up to 120 seconds)
  console.log('\n' + '='.repeat(60))
  console.log('  WAITING FOR YOU TO TYPE YOUR GEMINI API KEY')
  console.log('  Type it in the browser window that just opened.')
  console.log('='.repeat(60) + '\n')

  const apiKeyInput = page.getByTestId('api-key-input')
  await expect(apiKeyInput).toBeVisible()

  // Poll until the API key field has content (user types it manually)
  await expect(async () => {
    const value = await apiKeyInput.inputValue()
    expect(value.length).toBeGreaterThan(5)
  }).toPass({ timeout: 120_000, intervals: [1000] })

  await page.screenshot({ path: 'tests/screenshots/quality-03-key-entered.png' })

  // Step 4: Accept the safety confirmation dialog when it appears
  page.on('dialog', (dialog) => dialog.accept())

  // Step 5: Set up download listener BEFORE clicking generate
  const downloadPromise = page.waitForEvent('download', { timeout: 150_000 })

  // Step 6: Click Generate
  await page.getByTestId('generate-btn').click()
  console.log('Clicked Generate — waiting for Gemini response (this may take 30-90 seconds)...')

  // Step 7: Screenshot the loading state
  await page.waitForTimeout(1000)
  await page.screenshot({ path: 'tests/screenshots/quality-04-loading.png' })

  // Step 8: Wait for the download
  const download = await downloadPromise
  expect(download.suggestedFilename()).toBe('notebook.ipynb')

  // Save the downloaded file
  const outputPath = path.join(OUTPUT_DIR, 'attention-is-all-you-need.ipynb')
  await download.saveAs(outputPath)
  console.log(`Notebook saved to: ${outputPath}`)

  await page.screenshot({ path: 'tests/screenshots/quality-05-complete.png' })

  // ──────────────────────────────────────────────
  // NOTEBOOK VALIDATION
  // ──────────────────────────────────────────────

  const raw = fs.readFileSync(outputPath, 'utf-8')

  // V1: Valid JSON
  let notebook
  try {
    notebook = JSON.parse(raw)
  } catch (e) {
    throw new Error(`Downloaded file is not valid JSON: ${e.message}`)
  }

  // V2: Has nbformat 4
  expect(notebook.nbformat).toBe(4)
  console.log(`✓ nbformat: ${notebook.nbformat}`)

  // V3: Has cells array
  expect(Array.isArray(notebook.cells)).toBe(true)
  console.log(`✓ cells array present with ${notebook.cells.length} cells`)

  // V4: Has at least 20 cells
  expect(notebook.cells.length).toBeGreaterThanOrEqual(20)
  console.log(`✓ cell count: ${notebook.cells.length} (≥20)`)

  // V5: First cell is the safety disclaimer
  const firstCellSource = notebook.cells[0].source.join('')
  expect(firstCellSource.toLowerCase()).toContain('safety')
  console.log('✓ first cell is safety disclaimer')

  // V6: Has both markdown and code cells
  const markdownCells = notebook.cells.filter((c) => c.cell_type === 'markdown')
  const codeCells = notebook.cells.filter((c) => c.cell_type === 'code')
  expect(markdownCells.length).toBeGreaterThan(5)
  expect(codeCells.length).toBeGreaterThan(5)
  console.log(`✓ ${markdownCells.length} markdown cells, ${codeCells.length} code cells`)

  // V7: No empty source arrays
  for (const cell of notebook.cells) {
    const source = Array.isArray(cell.source) ? cell.source.join('') : cell.source
    // Allow empty markdown cells (some are spacers) but code cells should have content
    if (cell.cell_type === 'code') {
      expect(source.trim().length).toBeGreaterThan(0)
    }
  }
  console.log('✓ no empty code cells')

  // V8: Contains all 8 section keywords
  const allText = notebook.cells
    .map((c) => {
      const src = Array.isArray(c.source) ? c.source.join('') : c.source
      return src
    })
    .join('\n')

  const missingSections = []
  for (const pattern of REQUIRED_SECTIONS) {
    if (!pattern.test(allText)) {
      missingSections.push(pattern.source)
    }
  }
  if (missingSections.length > 0) {
    console.warn(`⚠ Missing section patterns: ${missingSections.join(', ')}`)
  }
  // Allow up to 2 missing (section names may vary)
  expect(missingSections.length).toBeLessThanOrEqual(2)
  console.log(`✓ ${8 - missingSections.length}/8 required sections found`)

  // V9: Code cells contain valid Python (use ast.parse)
  let validPython = 0
  let invalidPython = 0
  for (const cell of codeCells) {
    const source = Array.isArray(cell.source) ? cell.source.join('') : cell.source
    // Skip cells that start with ! (shell commands like !pip install)
    if (source.trim().startsWith('!')) {
      validPython++
      continue
    }
    try {
      execSync(`python3 -c "import ast; ast.parse(${JSON.stringify(source)})"`, {
        timeout: 5000,
        stdio: 'pipe',
      })
      validPython++
    } catch {
      invalidPython++
      console.warn(`⚠ Invalid Python in cell: ${source.substring(0, 80)}...`)
    }
  }
  console.log(`✓ Python validation: ${validPython} valid, ${invalidPython} invalid out of ${codeCells.length} code cells`)
  // Allow up to 20% invalid (Gemini sometimes generates imperfect syntax)
  expect(invalidPython).toBeLessThan(codeCells.length * 0.2)

  // Final summary
  console.log('\n' + '='.repeat(60))
  console.log('  NOTEBOOK QUALITY REPORT')
  console.log('='.repeat(60))
  console.log(`  Total cells:      ${notebook.cells.length}`)
  console.log(`  Markdown cells:   ${markdownCells.length}`)
  console.log(`  Code cells:       ${codeCells.length}`)
  console.log(`  Sections found:   ${8 - missingSections.length}/8`)
  console.log(`  Valid Python:     ${validPython}/${codeCells.length}`)
  console.log(`  Safety disclaimer: present`)
  console.log('='.repeat(60) + '\n')
})
