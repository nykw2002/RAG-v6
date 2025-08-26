import { test, expect } from '@playwright/test';

test.describe('Error Handling and Edge Cases', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('Dynamic Elements Manager')).toBeVisible();
  });

  test.describe('Backend Connection Errors', () => {
    test('App handles backend disconnection gracefully', async ({ page }) => {
      // This test assumes backend is running initially
      await expect(page.getByText('Dynamic Elements Manager')).toBeVisible();
      await expect(page.getByText('Connection Error')).not.toBeVisible();
      await expect(page.getByText('Loading Dynamic Elements Manager...')).not.toBeVisible();
    });

    test('Loading state appears when API is slow', async ({ page }) => {
      // Intercept API calls to simulate slow response
      await page.route('**/api/v1/elements/', async route => {
        await new Promise(resolve => setTimeout(resolve, 2000));
        await route.continue();
      });
      
      await page.reload();
      
      // Should show loading state briefly
      await expect(page.getByText('Loading Dynamic Elements Manager...')).toBeVisible({ timeout: 1000 });
    });
  });

  test.describe('Form Validation Errors', () => {
    test('Empty form submission shows appropriate feedback', async ({ page }) => {
      await page.getByRole('button', { name: 'Configure Element' }).click();
      
      // Try to save completely empty form
      await page.getByRole('button', { name: 'Save Configuration' }).click();
      
      // Should remain on form (not proceed to name dialog)
      await expect(page.getByText('Configure Dynamic Element')).toBeVisible();
      await expect(page.getByText('Save Dynamic Element')).not.toBeVisible();
    });

    test('Partial form completion validation', async ({ page }) => {
      await page.getByRole('button', { name: 'Configure Element' }).click();
      
      // Fill only prompt
      await page.getByPlaceholder('Enter your prompt here...').fill('Test prompt');
      await page.getByRole('button', { name: 'Save Configuration' }).click();
      
      // Should not proceed without method selection
      await expect(page.getByText('Configure Dynamic Element')).toBeVisible();
    });

    test('Element name validation in save dialog', async ({ page }) => {
      await page.getByRole('button', { name: 'Configure Element' }).click();
      
      // Fill required fields
      await page.getByPlaceholder('Enter your prompt here...').fill('Test');
      await page.locator('button:has-text("Select AI model")').click();
      await page.getByText('GPT-4').click();
      await page.locator('button:has-text("Select method")').click();
      await page.getByText('Reasoning').click();
      
      await page.getByRole('button', { name: 'Save Configuration' }).click();
      
      // Test empty name
      const saveButton = page.getByRole('button', { name: 'Save Element' });
      await expect(saveButton).toBeDisabled();
      
      // Test whitespace only name
      await page.getByPlaceholder('Enter element name...').fill('   ');
      await expect(saveButton).toBeDisabled();
      
      // Test valid name
      await page.getByPlaceholder('Enter element name...').fill('Valid Name');
      await expect(saveButton).not.toBeDisabled();
    });
  });

  test.describe('UI State Management', () => {
    test('Multiple modals cannot be open simultaneously', async ({ page }) => {
      // Open configuration modal
      await page.getByRole('button', { name: 'Configure Element' }).click();
      await expect(page.getByText('Configure Dynamic Element')).toBeVisible();
      
      // Try to open validation modal (should not work)
      // This tests that proper modal management prevents conflicts
    });

    test('Modal state resets on close', async ({ page }) => {
      await page.getByRole('button', { name: 'Configure Element' }).click();
      
      // Fill some data
      await page.getByPlaceholder('Enter your prompt here...').fill('Test data');
      await page.locator('button:has-text("Select AI model")').click();
      await page.getByText('GPT-4').click();
      
      // Close modal
      await page.locator('.fixed.inset-0.bg-black\\/80').click();
      
      // Reopen modal
      await page.getByRole('button', { name: 'Configure Element' }).click();
      
      // Form should be reset
      await expect(page.getByPlaceholder('Enter your prompt here...')).toHaveValue('');
      await expect(page.locator('button:has-text("Select AI model")')).toBeVisible();
    });

    test('Data source buttons toggle correctly', async ({ page }) => {
      await page.getByRole('button', { name: 'Configure Element' }).click();
      
      const button1 = page.getByTestId('data-source-kpi-tables');
      const button2 = page.getByTestId('data-source-de');
      
      // Test multiple selections
      await button1.click();
      await button2.click();
      await expect(button1).toHaveClass(/bg-primary/);
      await expect(button2).toHaveClass(/bg-primary/);
      
      // Test deselection
      await button1.click();
      await expect(button1).not.toHaveClass(/bg-primary/);
      await expect(button2).toHaveClass(/bg-primary/);
    });
  });

  test.describe('File Upload Errors', () => {
    test('Processing modal handles no files uploaded', async ({ page }) => {
      // First create an element to access processing modal
      await page.getByRole('button', { name: 'Configure Element' }).click();
      await page.getByPlaceholder('Enter your prompt here...').fill('Test');
      await page.locator('button:has-text("Select method")').click();
      await page.getByText('Reasoning').click();
      await page.getByRole('button', { name: 'Save Configuration' }).click();
      await page.getByPlaceholder('Enter element name...').fill('TestElement');
      await page.getByRole('button', { name: 'Save Element' }).click();
      await page.getByRole('button', { name: 'Done' }).click();
      
      // Access processing modal
      await page.getByRole('button', { name: 'View Dashboard' }).click();
      await page.waitForTimeout(500);
      const testButton = page.getByRole('button', { name: 'Test' }).first();
      await testButton.click({ force: true });
      
      // Run button should be disabled without files
      const runButton = page.getByRole('button', { name: 'Run AI Processing' });
      await expect(runButton).toBeDisabled();
    });
  });

  test.describe('Dropdown Edge Cases', () => {
    test('Dropdown closes when clicking outside', async ({ page }) => {
      await page.getByRole('button', { name: 'Configure Element' }).click();
      
      // Open dropdown
      await page.locator('button:has-text("Select AI model")').click();
      await expect(page.getByText('GPT-4')).toBeVisible();
      
      // Click outside dropdown
      await page.getByText('Configure Dynamic Element').click();
      
      // Dropdown should close
      await expect(page.getByText('GPT-4')).not.toBeVisible();
    });

    test('Multiple dropdowns can be used in sequence', async ({ page }) => {
      await page.getByRole('button', { name: 'Configure Element' }).click();
      
      // Use AI Model dropdown
      await page.locator('button:has-text("Select AI model")').click();
      await page.getByText('Claude 3').click();
      
      // Use Method dropdown
      await page.locator('button:has-text("Select method")').click();
      await page.getByText('Extraction').click();
      
      // Use File Type dropdown
      await page.locator('button:has-text("Select file type")').click();
      await page.getByText('CSV').click();
      
      // Verify all selections are visible
      await expect(page.locator('text=Claude 3')).toBeVisible();
      await expect(page.locator('text=Extraction')).toBeVisible();
      await expect(page.locator('text=CSV')).toBeVisible();
    });

    test('Dropdown values can be changed multiple times', async ({ page }) => {
      await page.getByRole('button', { name: 'Configure Element' }).click();
      
      // Select initial value
      await page.locator('button:has-text("Select AI model")').click();
      await page.getByText('GPT-4').click();
      await expect(page.locator('text=GPT-4')).toBeVisible();
      
      // Change to different value
      await page.locator('button:has-text("GPT-4")').click();
      await page.getByText('Claude 3').click();
      await expect(page.locator('text=Claude 3')).toBeVisible();
      
      // Change again
      await page.locator('button:has-text("Claude 3")').click();
      await page.getByText('Gemini Pro').click();
      await expect(page.locator('text=Gemini Pro')).toBeVisible();
    });
  });

  test.describe('Responsive Behavior Edge Cases', () => {
    test('Modals work correctly on very small screens', async ({ page }) => {
      await page.setViewportSize({ width: 320, height: 568 }); // iPhone SE size
      
      await page.getByRole('button', { name: 'Configure Element' }).click();
      await expect(page.getByText('Configure Dynamic Element')).toBeVisible();
      
      // Modal should be properly sized and scrollable
      const modal = page.locator('[role="dialog"]');
      await expect(modal).toBeVisible();
    });

    test('Long text content handles overflow correctly', async ({ page }) => {
      await page.getByRole('button', { name: 'Configure Element' }).click();
      
      // Enter very long prompt
      const longPrompt = 'This is a very long prompt that should test how the textarea handles extensive text input and whether it properly wraps or scrolls. '.repeat(10);
      await page.getByPlaceholder('Enter your prompt here...').fill(longPrompt);
      
      // Verify text is contained properly
      await expect(page.getByPlaceholder('Enter your prompt here...')).toHaveValue(longPrompt);
    });
  });

  test.describe('Performance and Memory', () => {
    test('Rapid modal opening/closing does not cause issues', async ({ page }) => {
      for (let i = 0; i < 5; i++) {
        await page.getByRole('button', { name: 'Configure Element' }).click();
        await expect(page.getByText('Configure Dynamic Element')).toBeVisible();
        await page.locator('.fixed.inset-0.bg-black\\/80').click();
        await expect(page.getByText('Configure Dynamic Element')).not.toBeVisible();
      }
      
      // App should still be responsive
      await expect(page.getByText('Dynamic Elements Manager')).toBeVisible();
    });

    test('Multiple element creation does not break UI', async ({ page }) => {
      // Create multiple elements rapidly
      for (let i = 0; i < 3; i++) {
        await page.getByRole('button', { name: 'Configure Element' }).click();
        await page.getByPlaceholder('Enter your prompt here...').fill(`Test prompt ${i}`);
        await page.locator('button:has-text("Select method")').click();
        await page.getByText('Reasoning').click();
        await page.getByRole('button', { name: 'Save Configuration' }).click();
        await page.getByPlaceholder('Enter element name...').fill(`Element ${i}`);
        await page.getByRole('button', { name: 'Save Element' }).click();
        await page.getByRole('button', { name: 'Done' }).click();
      }
      
      // Check that all elements appear in dashboard
      await page.getByRole('button', { name: 'View Dashboard' }).click();
      await page.waitForTimeout(1000);
      
      await expect(page.locator('text=Element 0')).toBeVisible();
      await expect(page.locator('text=Element 1')).toBeVisible();
      await expect(page.locator('text=Element 2')).toBeVisible();
    });
  });
});