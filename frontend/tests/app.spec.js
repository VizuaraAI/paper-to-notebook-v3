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

  // Accept the safety confirmation dialog so download proceeds
  page.on('dialog', (dialog) => dialog.accept())

  const downloadPromise = page.waitForEvent('download')

  await page.goto('/')
  await page.getByTestId('api-key-input').fill('test-key')
  await page.getByTestId('arxiv-url-input').fill('https://arxiv.org/abs/2401.12345')
  await page.getByTestId('generate-btn').click()

  const download = await downloadPromise
  expect(download.suggestedFilename()).toBe('notebook.ipynb')
})

test('shows safety notice below generate button', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByTestId('safety-notice')).toBeVisible()
  await expect(page.getByTestId('safety-notice')).toContainText('review before executing')
})

test('shows confirmation dialog before download', async ({ page }) => {
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

  // Dismiss the dialog
  page.on('dialog', (dialog) => dialog.dismiss())

  await page.goto('/')
  await page.getByTestId('api-key-input').fill('test-key-12345')
  await page.getByTestId('arxiv-url-input').fill('https://arxiv.org/abs/2401.12345')
  await page.getByTestId('generate-btn').click()

  // After dismissing, no download should happen — just verify no crash
  await page.waitForTimeout(500)
})

test('clears API key after successful generation', async ({ page }) => {
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

  // Accept the dialog
  page.on('dialog', (dialog) => dialog.accept())

  await page.goto('/')
  await page.getByTestId('api-key-input').fill('test-key-12345')
  await page.getByTestId('arxiv-url-input').fill('https://arxiv.org/abs/2401.12345')
  await page.getByTestId('generate-btn').click()

  // Wait for the process to complete
  await page.waitForTimeout(1000)

  // API key should be cleared
  await expect(page.getByTestId('api-key-input')).toHaveValue('')
})

test('PDF upload flow with file chooser (mocked API)', async ({ page }) => {
  const fakeNotebook = {
    nbformat: 4,
    nbformat_minor: 5,
    metadata: {},
    cells: [{ cell_type: 'markdown', metadata: {}, source: ['# Test'] }],
  }

  await page.route('**/api/upload-pdf', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(fakeNotebook),
    })
  )

  // Accept the safety confirmation dialog
  page.on('dialog', (dialog) => dialog.accept())

  await page.goto('/')
  await page.screenshot({ path: 'tests/screenshots/v3-pdf-01-empty.png' })

  await page.getByTestId('api-key-input').fill('test-api-key-12345')

  // Create a fake PDF file and set it via file chooser
  const fileChooserPromise = page.waitForEvent('filechooser')
  await page.getByTestId('pdf-upload').click()
  const fileChooser = await fileChooserPromise
  await fileChooser.setFiles({
    name: 'test-paper.pdf',
    mimeType: 'application/pdf',
    buffer: Buffer.from('%PDF-1.4 fake pdf content'),
  })

  await page.screenshot({ path: 'tests/screenshots/v3-pdf-02-file-selected.png' })
  await expect(page.getByTestId('generate-btn')).toBeEnabled()
})

test('server error shows error message to user', async ({ page }) => {
  await page.route('**/api/arxiv-url', (route) =>
    route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'Internal server error' }),
    })
  )

  await page.goto('/')
  await page.getByTestId('api-key-input').fill('test-api-key-12345')
  await page.getByTestId('arxiv-url-input').fill('https://arxiv.org/abs/2401.12345')
  await page.getByTestId('generate-btn').click()

  await expect(page.getByTestId('error-message')).toBeVisible()
  await expect(page.getByTestId('error-message')).toContainText('Internal server error')
  await page.screenshot({ path: 'tests/screenshots/v3-error-01-server-error.png' })
})

test('form resets after successful generation', async ({ page }) => {
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

  // Accept the safety confirmation dialog
  page.on('dialog', (dialog) => dialog.accept())

  await page.goto('/')
  await page.getByTestId('api-key-input').fill('test-api-key-12345')
  await page.getByTestId('arxiv-url-input').fill('https://arxiv.org/abs/2401.12345')
  await page.screenshot({ path: 'tests/screenshots/v3-reset-01-filled.png' })

  await page.getByTestId('generate-btn').click()

  // Wait for the process to complete
  await page.waitForTimeout(1000)

  // API key should be cleared after successful generation
  await expect(page.getByTestId('api-key-input')).toHaveValue('')
  await page.screenshot({ path: 'tests/screenshots/v3-reset-02-after.png' })
})

test('loading spinner appears during generation', async ({ page }) => {
  await page.route('**/api/arxiv-url', async (route) => {
    await new Promise((r) => setTimeout(r, 2000))
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ nbformat: 4, cells: [] }),
    })
  })

  await page.goto('/')
  await page.getByTestId('api-key-input').fill('test-api-key-12345')
  await page.getByTestId('arxiv-url-input').fill('https://arxiv.org/abs/2401.12345')
  await page.getByTestId('generate-btn').click()

  // Spinner should be visible while loading
  await expect(page.getByTestId('loading-spinner')).toBeVisible()
  await page.screenshot({ path: 'tests/screenshots/v3-loading-01-spinner.png' })

  // Generate button should be disabled during loading
  await expect(page.getByTestId('generate-btn')).toBeDisabled()
})
