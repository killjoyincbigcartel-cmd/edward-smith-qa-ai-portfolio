import { test, expect } from '@playwright/test';

const baseUrl = process.env.BASE_URL ?? 'http://localhost:5173';

test.describe('registration validation', () => {
  test('rejects an invalid email address', async ({ page }) => {
    await page.goto(`${baseUrl}/register`);

    await page.getByLabel('Email').fill('customer@');
    await page.getByLabel('Password').fill('ValidPassword123!');
    await page.getByLabel('Confirm password').fill('ValidPassword123!');
    await page.getByRole('button', { name: /register|sign up|create account/i }).click();

    await expect(page.getByText(/valid email|invalid email|email address/i)).toBeVisible();
  });
});

// Before running this example, map the route, labels, and expected message to
// the application under test. The selectors are intentionally accessible-first.
