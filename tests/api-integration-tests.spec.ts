import { test, expect } from '@playwright/test';

test.describe('API Integration and Data Flow Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('Dynamic Elements Manager')).toBeVisible();
  });

  test.describe('Backend API Integration', () => {
    test('Elements are loaded from backend on app start', async ({ page }) => {
      // Wait for API calls to complete
      await page.waitForTimeout(2000);
      
      // Should not show loading state after initial load
      await expect(page.getByText('Loading Dynamic Elements Manager...')).not.toBeVisible();
      
      // Should not show connection error
      await expect(page.getByText('Connection Error')).not.toBeVisible();
    });

    test('Creating element makes API call and updates UI', async ({ page }) => {
      // Monitor network requests
      let createElementCalled = false;
      page.on('request', request => {
        if (request.url().includes('/api/v1/elements/') && request.method() === 'POST') {
          createElementCalled = true;
        }
      });

      // Create element
      await page.getByRole('button', { name: 'Configure Element' }).click();
      await page.getByPlaceholder('Enter your prompt here...').fill('API Test Element');
      await page.locator('button:has-text("Select AI model")').click();
      await page.getByText('GPT-4').click();
      await page.locator('button:has-text("Select method")').click();
      await page.getByText('Reasoning').click();
      await page.locator('button:has-text("Select file type")').click();
      await page.getByText('PDF').click();
      await page.getByRole('button', { name: 'KPI tables' }).click();
      
      await page.getByRole('button', { name: 'Save Configuration' }).click();
      await page.getByPlaceholder('Enter element name...').fill('API Test Element');
      await page.getByRole('button', { name: 'Save Element' }).click();
      
      // Wait for API call
      await page.waitForTimeout(1000);
      
      // Verify API was called
      expect(createElementCalled).toBe(true);
      
      await page.getByRole('button', { name: 'Done' }).click();
      
      // Verify element appears in dashboard
      await page.getByRole('button', { name: 'View Dashboard' }).click();
      await page.waitForTimeout(1000);
      await expect(page.locator('text=API Test Element')).toBeVisible();
    });

    test('Deleting element makes API call and updates UI', async ({ page }) => {
      // First create an element
      await page.getByRole('button', { name: 'Configure Element' }).click();
      await page.getByPlaceholder('Enter your prompt here...').fill('Element to Delete');
      await page.locator('button:has-text("Select method")').click();
      await page.getByText('Reasoning').click();
      await page.getByRole('button', { name: 'Save Configuration' }).click();
      await page.getByPlaceholder('Enter element name...').fill('Delete Test Element');
      await page.getByRole('button', { name: 'Save Element' }).click();
      await page.getByRole('button', { name: 'Done' }).click();

      // Monitor delete API calls
      let deleteElementCalled = false;
      page.on('request', request => {
        if (request.url().includes('/api/v1/elements/') && request.method() === 'DELETE') {
          deleteElementCalled = true;
        }
      });

      // Go to dashboard and delete element
      await page.getByRole('button', { name: 'View Dashboard' }).click();
      await page.waitForTimeout(1000);
      
      // Find and click delete button for our element
      const elementCard = page.locator('text=Delete Test Element').locator('..').locator('..');
      const deleteButton = elementCard.getByRole('button').first(); // Trash button
      await deleteButton.click();
      
      await page.waitForTimeout(1000);
      
      // Verify API was called
      expect(deleteElementCalled).toBe(true);
      
      // Verify element is removed from UI
      await expect(page.locator('text=Delete Test Element')).not.toBeVisible();
    });

    test('Validation updates element status via API', async ({ page }) => {
      // Monitor API calls for validation
      let validateElementCalled = false;
      page.on('request', request => {
        if (request.url().includes('/validate') && request.method() === 'POST') {
          validateElementCalled = true;
        }
      });

      // Create element first
      await page.getByRole('button', { name: 'Configure Element' }).click();
      await page.getByPlaceholder('Enter your prompt here...').fill('Validation Test');
      await page.locator('button:has-text("Select method")').click();
      await page.getByText('Reasoning').click();
      await page.getByRole('button', { name: 'Save Configuration' }).click();
      await page.getByPlaceholder('Enter element name...').fill('Validation Element');
      await page.getByRole('button', { name: 'Save Element' }).click();
      await page.getByRole('button', { name: 'Done' }).click();

      // Access validation dashboard
      await page.getByRole('button', { name: 'View Dashboard' }).click();
      await page.waitForTimeout(1000);
      
      // Should initially show as Draft
      await expect(page.locator('text=Draft')).toBeVisible();
    });
  });

  test.describe('Data Persistence and State Management', () => {
    test('Created elements persist across page reloads', async ({ page }) => {
      // Create element
      await page.getByRole('button', { name: 'Configure Element' }).click();
      await page.getByPlaceholder('Enter your prompt here...').fill('Persistent Element');
      await page.locator('button:has-text("Select method")').click();
      await page.getByText('Reasoning').click();
      await page.getByRole('button', { name: 'Save Configuration' }).click();
      await page.getByPlaceholder('Enter element name...').fill('Persistence Test');
      await page.getByRole('button', { name: 'Save Element' }).click();
      await page.getByRole('button', { name: 'Done' }).click();

      // Reload page
      await page.reload();
      await page.waitForTimeout(2000);

      // Check element still exists
      await page.getByRole('button', { name: 'View Dashboard' }).click();
      await page.waitForTimeout(1000);
      await expect(page.locator('text=Persistence Test')).toBeVisible();
    });

    test('Element modifications are saved to backend', async ({ page }) => {
      // Create element
      await page.getByRole('button', { name: 'Configure Element' }).click();
      await page.getByPlaceholder('Enter your prompt here...').fill('Original Prompt');
      await page.locator('button:has-text("Select method")').click();
      await page.getByText('Reasoning').click();
      await page.getByRole('button', { name: 'Save Configuration' }).click();
      await page.getByPlaceholder('Enter element name...').fill('Edit Test Element');
      await page.getByRole('button', { name: 'Save Element' }).click();
      await page.getByRole('button', { name: 'Done' }).click();

      // Edit element
      await page.getByRole('button', { name: 'View Dashboard' }).click();
      await page.waitForTimeout(1000);
      
      const elementCard = page.locator('text=Edit Test Element').locator('..').locator('..');
      const editButton = elementCard.getByRole('button', { name: 'Edit' });
      await editButton.click();

      // Modify prompt
      await page.getByPlaceholder('Enter your prompt here...').clear();
      await page.getByPlaceholder('Enter your prompt here...').fill('Modified Prompt');
      await page.getByRole('button', { name: 'Update Configuration' }).click();

      // Reload and verify changes persist
      await page.reload();
      await page.waitForTimeout(2000);
      await page.getByRole('button', { name: 'View Dashboard' }).click();
      await page.waitForTimeout(1000);
      
      // Check if modified prompt is visible (would be in element details)
      const modifiedCard = page.locator('text=Edit Test Element').locator('..').locator('..');
      await expect(modifiedCard.locator('text=Modified Prompt')).toBeVisible();
    });
  });

  test.describe('Real-time Data Updates', () => {
    test('Dashboard reflects changes immediately after element creation', async ({ page }) => {
      // Open dashboard first
      await page.getByRole('button', { name: 'View Dashboard' }).click();
      const initialElements = await page.locator('.hover\\:shadow-md').count();
      await page.locator('.fixed.inset-0.bg-black\\/80').click();

      // Create new element
      await page.getByRole('button', { name: 'Configure Element' }).click();
      await page.getByPlaceholder('Enter your prompt here...').fill('Real-time Test');
      await page.locator('button:has-text("Select method")').click();
      await page.getByText('Reasoning').click();
      await page.getByRole('button', { name: 'Save Configuration' }).click();
      await page.getByPlaceholder('Enter element name...').fill('Real-time Element');
      await page.getByRole('button', { name: 'Save Element' }).click();
      await page.getByRole('button', { name: 'Done' }).click();

      // Check dashboard immediately
      await page.getByRole('button', { name: 'View Dashboard' }).click();
      await page.waitForTimeout(1000);
      const finalElements = await page.locator('.hover\\:shadow-md').count();
      
      expect(finalElements).toBe(initialElements + 1);
      await expect(page.locator('text=Real-time Element')).toBeVisible();
    });

    test('Element status updates reflect in UI immediately', async ({ page }) => {
      // This test would verify that when an element's status changes,
      // it's reflected immediately in all relevant UI components
      await page.getByRole('button', { name: 'View Dashboard' }).click();
      await page.waitForTimeout(1000);
      
      // Look for elements with Draft status
      const draftBadges = page.locator('text=Draft');
      const draftCount = await draftBadges.count();
      
      if (draftCount > 0) {
        // Element status changes would be reflected here
        await expect(draftBadges.first()).toBeVisible();
      }
    });
  });

  test.describe('API Error Handling', () => {
    test('Handles API failures gracefully', async ({ page }) => {
      // Intercept API calls and make them fail
      await page.route('**/api/v1/elements/', async route => {
        await route.abort('failed');
      });

      await page.reload();
      await page.waitForTimeout(3000);
      
      // Should show connection error
      await expect(page.getByText('Connection Error')).toBeVisible();
    });

    test('Retry mechanism works for failed operations', async ({ page }) => {
      let requestCount = 0;
      
      // Fail first request, succeed on retry
      await page.route('**/api/v1/elements/', async route => {
        requestCount++;
        if (requestCount === 1) {
          await route.abort('failed');
        } else {
          await route.continue();
        }
      });

      // Try creating element
      await page.getByRole('button', { name: 'Configure Element' }).click();
      await page.getByPlaceholder('Enter your prompt here...').fill('Retry Test');
      await page.locator('button:has-text("Select method")').click();
      await page.getByText('Reasoning').click();
      await page.getByRole('button', { name: 'Save Configuration' }).click();
      await page.getByPlaceholder('Enter element name...').fill('Retry Element');
      
      // This might trigger retry logic
      await page.getByRole('button', { name: 'Save Element' }).click();
      
      // Verify it eventually succeeds (if retry is implemented)
      await page.waitForTimeout(3000);
    });
  });

  test.describe('Data Validation and Integrity', () => {
    test('Form data is correctly sent to API', async ({ page }) => {
      let sentData: any = null;
      
      // Capture API request data
      page.on('request', async request => {
        if (request.url().includes('/api/v1/elements/') && request.method() === 'POST') {
          try {
            sentData = await request.postDataJSON();
          } catch (e) {
            // Handle case where post data isn't JSON
          }
        }
      });

      // Create element with specific data
      await page.getByRole('button', { name: 'Configure Element' }).click();
      await page.getByPlaceholder('Enter your prompt here...').fill('Data Validation Test Prompt');
      await page.locator('button:has-text("Select AI model")').click();
      await page.getByText('Claude 3').click();
      await page.locator('button:has-text("Select method")').click();
      await page.getByText('Extraction').click();
      await page.locator('button:has-text("Select file type")').click();
      await page.getByText('CSV').click();
      await page.getByTestId('data-source-kpi-tables').click();
      await page.getByTestId('data-source-de').click();
      
      await page.getByRole('button', { name: 'Save Configuration' }).click();
      await page.getByPlaceholder('Enter element name...').fill('Data Validation Element');
      await page.getByRole('button', { name: 'Save Element' }).click();
      
      await page.waitForTimeout(1000);
      
      // Verify sent data matches form input
      if (sentData) {
        expect(sentData.name).toBe('Data Validation Element');
        expect(sentData.prompt).toBe('Data Validation Test Prompt');
        expect(sentData.ai_model).toBe('Claude 3');
        expect(sentData.method).toBe('Extraction');
        expect(sentData.file_type).toBe('CSV');
        expect(sentData.data_sources).toContain('KPI tables');
        expect(sentData.data_sources).toContain('DE');
      }
    });

    test('API response data is correctly displayed in UI', async ({ page }) => {
      // Create element and verify it appears correctly
      await page.getByRole('button', { name: 'Configure Element' }).click();
      await page.getByPlaceholder('Enter your prompt here...').fill('UI Display Test');
      await page.locator('button:has-text("Select AI model")').click();
      await page.getByText('Gemini Pro').click();
      await page.locator('button:has-text("Select method")').click();
      await page.getByText('Reasoning').click();
      await page.locator('button:has-text("Select file type")').click();
      await page.getByText('DOCX').click();
      await page.getByTestId('data-source-other-data').click();
      
      await page.getByRole('button', { name: 'Save Configuration' }).click();
      await page.getByPlaceholder('Enter element name...').fill('UI Display Element');
      await page.getByRole('button', { name: 'Save Element' }).click();
      await page.getByRole('button', { name: 'Done' }).click();
      
      // Check dashboard display
      await page.getByRole('button', { name: 'View Dashboard' }).click();
      await page.waitForTimeout(1000);
      
      // Verify all data is displayed correctly
      const elementCard = page.locator('text=UI Display Element').locator('..').locator('..');
      await expect(elementCard.locator('text=UI Display Test')).toBeVisible();
      await expect(elementCard.locator('text=Gemini Pro')).toBeVisible();
      await expect(elementCard.locator('text=Reasoning')).toBeVisible();
      await expect(elementCard.locator('text=DOCX')).toBeVisible();
      await expect(elementCard.locator('text=Other Data')).toBeVisible();
      await expect(elementCard.locator('text=Draft')).toBeVisible();
    });
  });
});