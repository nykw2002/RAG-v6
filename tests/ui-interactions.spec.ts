import { test, expect } from '@playwright/test';

test.describe('UI Interactions', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Wait for the app to load
    await expect(page.getByText('Dynamic Elements Manager')).toBeVisible();
  });

  test('Configuration modal opens and dropdowns work', async ({ page }) => {
    // Open configuration modal
    await page.getByRole('button', { name: 'Configure Element' }).click();
    
    // Wait for modal to be visible
    await expect(page.getByText('Configure Dynamic Element')).toBeVisible();
    
    // Test AI Model dropdown
    await page.locator('button:has-text("Select AI model")').click();
    await expect(page.getByText('GPT-4')).toBeVisible();
    await page.getByText('GPT-4').click();
    
    // Verify selection shows in trigger (wait a moment for state update)
    await page.waitForTimeout(100);
    await expect(page.locator('text=GPT-4')).toBeVisible();
    
    // Test Method dropdown
    await page.locator('button:has-text("Select method")').click();
    await expect(page.getByText('Reasoning')).toBeVisible();
    await page.getByText('Reasoning').click();
    
    // Verify selection shows in trigger
    await page.waitForTimeout(100);
    await expect(page.locator('text=Reasoning')).toBeVisible();
    
    // Test File Type dropdown
    await page.locator('button:has-text("Select file type")').click();
    await expect(page.getByText('PDF')).toBeVisible();
    await page.getByText('PDF').click();
    
    // Verify selection shows in trigger
    await page.waitForTimeout(100);
    await expect(page.locator('text=PDF')).toBeVisible();
    
    // Test data source buttons
    await page.getByRole('button', { name: 'KPI tables' }).click();
    await expect(page.getByRole('button', { name: 'KPI tables' })).toHaveClass(/bg-primary/);
    
    // Fill prompt
    await page.getByPlaceholder('Enter your prompt here...').fill('Test prompt for validation');
    
    // Save configuration
    await page.getByRole('button', { name: 'Save Configuration' }).click();
    
    // Should show name dialog
    await expect(page.getByText('Save Dynamic Element')).toBeVisible();
    await page.getByPlaceholder('Enter element name...').fill('Test Element');
    await page.getByRole('button', { name: 'Save Element' }).click();
    
    // Should show preview
    await expect(page.getByText('Developer Preview')).toBeVisible();
    await expect(page.getByText('Configuration saved successfully!')).toBeVisible();
  });

  test('Validation modal opens and displays elements', async ({ page }) => {
    // Open validation modal
    await page.getByRole('button', { name: 'View Dashboard' }).click();
    
    // Wait for modal to be visible
    await expect(page.getByText('Dynamic Elements Dashboard')).toBeVisible();
    
    // Check if elements are displayed (there should be some from the backend)
    await expect(page.getByRole('heading', { name: 'Dynamic Elements', exact: true })).toBeVisible();
    
    // Close modal by clicking at top-left corner of backdrop (outside modal content)
    await page.mouse.click(50, 50);
    await expect(page.getByText('Dynamic Elements Dashboard')).not.toBeVisible();
  });

  test('Calibration modal opens correctly', async ({ page }) => {
    // Open calibration modal
    await page.getByRole('button', { name: 'Open Testing Suite' }).click();
    
    // Wait for modal to be visible
    await expect(page.getByText('Calibration & E2E Testing')).toBeVisible();
    
    // Close modal by clicking at top-left corner of backdrop (outside modal content)
    await page.mouse.click(50, 50);
    await expect(page.getByText('Calibration & E2E Testing')).not.toBeVisible();
  });

  test('Responsive design works on mobile viewport', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Check if elements are still accessible
    await expect(page.getByText('Dynamic Elements Manager')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Configure Element' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'View Dashboard' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Open Testing Suite' })).toBeVisible();
    
    // Test modal responsiveness
    await page.getByRole('button', { name: 'Configure Element' }).click();
    await expect(page.getByText('Configure Dynamic Element')).toBeVisible();
  });

  test('API connectivity works', async ({ page }) => {
    // Check if page loads without errors (indicates backend connectivity)
    await expect(page.getByText('Dynamic Elements Manager')).toBeVisible();
    
    // Should not show connection error
    await expect(page.getByText('Connection Error')).not.toBeVisible();
    
    // Should not be stuck on loading
    await expect(page.getByText('Loading Dynamic Elements Manager...')).not.toBeVisible();
  });
});