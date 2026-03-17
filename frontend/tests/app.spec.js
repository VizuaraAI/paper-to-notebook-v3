import { test, expect } from '@playwright/test'

test('shows title and form elements', async ({ page }) => {
  await page.goto('/')
  await page.screenshot({ path: 'tests/screenshots/task7-1-initial.png' })

  await expect(page.getByTestId('title')).toHaveText('Paper to Notebook')
  await expect(page.getByTestId('api-key-input')).toBeVisible()
  await expect(page.getByTestId('pdf-upload')).toBeVisible()
  await expect(page.getByTestId('arxiv-url-input')).toBeVisible()
  await expect(page.getByTestId('generate-btn')).toBeVisible()
})

test('generate button is disabled without inputs', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByTestId('generate-btn')).toBeDisabled()
})

test('generate button enables with api key and url', async ({ page }) => {
  await page.goto('/')
  await page.getByTestId('api-key-input').fill('test-key')
  await page.getByTestId('arxiv-url-input').fill('https://arxiv.org/abs/2401.12345')
  await page.screenshot({ path: 'tests/screenshots/task7-2-filled.png' })
  await expect(page.getByTestId('generate-btn')).toBeEnabled()
})

test('api key input is masked (password type)', async ({ page }) => {
  await page.goto('/')
  const input = page.getByTestId('api-key-input')
  await expect(input).toHaveAttribute('type', 'password')
})

test('shows loading spinner during API call', async ({ page }) => {
  // Mock the API to delay response
  await page.route('**/api/arxiv-url', async (route) => {
    await new Promise((r) => setTimeout(r, 1000))
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ nbformat: 4, cells: [] }),
    })
  })

  await page.goto('/')
  await page.getByTestId('api-key-input').fill('test-key')
  await page.getByTestId('arxiv-url-input').fill('https://arxiv.org/abs/2401.12345')
  await page.getByTestId('generate-btn').click()

  await expect(page.getByTestId('loading-spinner')).toBeVisible()
  await page.screenshot({ path: 'tests/screenshots/task8-1-loading.png' })
})

test('shows error message on API failure', async ({ page }) => {
  await page.route('**/api/arxiv-url', (route) =>
    route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'Test error message' }),
    })
  )

  await page.goto('/')
  await page.getByTestId('api-key-input').fill('test-key')
  await page.getByTestId('arxiv-url-input').fill('https://arxiv.org/abs/2401.12345')
  await page.getByTestId('generate-btn').click()

  await expect(page.getByTestId('error-message')).toHaveText('Test error message')
  await page.screenshot({ path: 'tests/screenshots/task8-2-error.png' })
})

test('triggers download on successful API response', async ({ page }) => {
  const fakeNotebook = {
    nbformat: 4,
    nbformat_minor: 5,
    metadata: {},
    cells: [{ cell_type: 'markdown', metadata: {}, source: ['# Test'] }],
  }

  await page.route('**/api/arxiv-url', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(fakeNotebook),
    })
  )

  const downloadPromise = page.waitForEvent('download')

  await page.goto('/')
  await page.getByTestId('api-key-input').fill('test-key')
  await page.getByTestId('arxiv-url-input').fill('https://arxiv.org/abs/2401.12345')
  await page.getByTestId('generate-btn').click()

  const download = await downloadPromise
  expect(download.suggestedFilename()).toBe('notebook.ipynb')
})
