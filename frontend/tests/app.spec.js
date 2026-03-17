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
