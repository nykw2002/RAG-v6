import { test, expect } from '@playwright/test';

test.describe('AI Integration Flows - Real Data Testing', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application and wait for load
    await page.goto('http://localhost:3005');
    await page.waitForSelector('text=Dynamic Elements Manager');
    
    // Ensure no modals are open by pressing Escape a few times
    await page.keyboard.press('Escape');
    await page.keyboard.press('Escape');
    await page.waitForTimeout(1000);
    
    // Wait for main page to be ready
    await page.waitForSelector('text=Configure Element');
  });

  test('Complete Extraction Flow - Find 14 Israel Complaints', async ({ page }) => {
    console.log('🧪 Testing Extraction Method (Script Generation) Flow');
    
    // Step 1: Create new element with extraction method
    await page.click('text=Configure Element');
    await page.waitForSelector('text=Select AI Model');
    
    // Configure element
    await page.fill('textarea[placeholder="Enter your prompt here..."]', 'Please tell me how many complaints are for Israel, i need a full list.');
    
    // Select extraction method
    await page.locator('text=Select Method').click();
    await page.click('text=Extraction');
    
    // Select AI model
    await page.locator('text=Select AI Model').click();
    await page.click('text=GPT-4');
    
    // Select file type
    await page.locator('text=Select File Type').click();
    await page.click('text=TXT');
    
    // Click Next to proceed to save
    await page.click('text=Next');
    await page.waitForSelector('input[placeholder="Enter element name..."]');
    
    // Enter element name and save
    await page.fill('input[placeholder="Enter element name..."]', 'Israel Complaints Extraction Test');
    await page.click('text=Save Element');
    
    // Wait for save completion and open dashboard
    await page.waitForSelector('text=Configure Element', { timeout: 5000 });
    await page.click('text=View Dashboard');
    await page.waitForSelector('[data-testid="validation-modal"]');
    
    // Step 2: Find and verify the created element
    const elementCard = page.locator('.grid').locator('.hover\\:shadow-md').first();
    await expect(elementCard.locator('text=Israel Complaints Extraction Test')).toBeVisible();
    await expect(elementCard.locator('text=extraction')).toBeVisible();
    
    // Step 3: Run processing with file upload by clicking Test button
    await elementCard.locator('text=Test').click();
    await page.waitForSelector('text=Upload Files');
    
    // Upload test.txt file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('test.txt');
    
    // Wait for file to be uploaded and click Run Analysis
    await page.waitForSelector('text=test.txt');
    await page.click('text=Run Analysis');
    
    // Wait for analysis to complete (give it up to 90 seconds for real AI processing)
    await page.waitForSelector('text=AI Analysis Results', { timeout: 90000 });
    
    // Step 4: Verify results
    const resultsSection = page.locator('text=AI Analysis Results').locator('..');
    const aiOutput = await resultsSection.textContent();
    console.log('📊 Extraction Method Output:', aiOutput);
    
    // Validate the expected results
    expect(aiOutput).toContain('14');
    expect(aiOutput).toContain('Israel');
    expect(aiOutput).toContain('000201357115');
    expect(aiOutput).toContain('complaints');
    
    console.log('✅ Extraction method successfully found Israel complaints');
    
    // Close modal
    await page.keyboard.press('Escape');
  });

  test('Complete Reasoning Flow - Complaint Trend Analysis', async ({ page }) => {
    console.log('🧪 Testing Reasoning Method (RAG Analysis) Flow');
    
    // Step 1: Create new element with reasoning method
    await page.click('text=Configure Element');
    await page.waitForSelector('text=Select AI Model');
    
    // Configure element with reasoning prompt
    await page.fill('textarea[placeholder="Enter your prompt here..."]', 'Analyze overall complaint numbers and compare to previous period. State the total number of substantiated and unsubstantiated complaints during the review period. Do NOT provide PPM analysis - only state counts. Compare to previous review period using phrasing: "The number of substantiated complaints increased/decreased/remained the same compared to the last period". If negative trend identified, summarize any CAPA implemented or ongoing.');
    
    // Select reasoning method
    await page.locator('text=Select Method').click();
    await page.click('text=Reasoning');
    
    // Select AI model
    await page.locator('text=Select AI Model').click();
    await page.click('text=GPT-4');
    
    // Select file type
    await page.locator('text=Select File Type').click();
    await page.click('text=TXT');
    
    // Click Next to proceed to save
    await page.click('text=Next');
    await page.waitForSelector('input[placeholder="Enter element name..."]');
    
    // Enter element name and save
    await page.fill('input[placeholder="Enter element name..."]', 'Complaint Trend Analysis Test');
    await page.click('text=Save Element');
    
    // Wait for save completion and open dashboard
    await page.waitForSelector('text=Configure Element', { timeout: 5000 });
    await page.click('text=View Dashboard');
    await page.waitForSelector('[data-testid="validation-modal"]');
    
    // Step 2: Find and verify the created element
    const elementCard = page.locator('.grid').locator('.hover\\:shadow-md').first();
    await expect(elementCard.locator('text=Complaint Trend Analysis Test')).toBeVisible();
    await expect(elementCard.locator('text=reasoning')).toBeVisible();
    
    // Step 3: Run processing with file upload by clicking Test button
    await elementCard.locator('text=Test').click();
    await page.waitForSelector('text=Upload Files');
    
    // Upload test.txt file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('test.txt');
    
    // Wait for file to be uploaded and click Run Analysis
    await page.waitForSelector('text=test.txt');
    await page.click('text=Run Analysis');
    
    // Wait for analysis to complete (give it up to 90 seconds for real AI processing)
    await page.waitForSelector('text=AI Analysis Results', { timeout: 90000 });
    
    // Step 4: Verify results
    const resultsSection = page.locator('text=AI Analysis Results').locator('..');
    const aiOutput = await resultsSection.textContent();
    console.log('📊 Reasoning Method Output:', aiOutput);
    
    // Validate the expected trend analysis patterns
    const hasCurrentPeriodData = aiOutput?.includes('substantiated') && aiOutput?.includes('unsubstantiated');
    const hasTrendAnalysis = aiOutput?.includes('increased') || aiOutput?.includes('decreased') || aiOutput?.includes('remained the same');
    const hasComplaintCounts = /\d+\s+substantiated/.test(aiOutput || '');
    
    expect(hasCurrentPeriodData).toBeTruthy();
    expect(hasTrendAnalysis).toBeTruthy(); 
    expect(hasComplaintCounts).toBeTruthy();
    
    console.log('✅ Reasoning method successfully provided complaint trend analysis');
    
    // Close modal
    await page.keyboard.press('Escape');
  });

  test('Comparison Test - Both Methods with Same Data', async ({ page }) => {
    console.log('🧪 Testing Both Methods Side by Side');
    
    let extractionResult = '';
    let reasoningResult = '';
    
    // Test extraction method
    {
      await page.click('text=Configure Element');
      await page.waitForSelector('text=Select AI Model');
      
      await page.fill('textarea[placeholder="Enter your prompt here..."]', 'How many complaints are for Israel?');
      
      await page.locator('text=Select Method').click();
      await page.click('text=Extraction');
      
      await page.locator('text=Select AI Model').click();
      await page.click('text=GPT-4');
      
      await page.locator('text=Select File Type').click();
      await page.click('text=TXT');
      
      await page.click('text=Next');
      await page.waitForSelector('input[placeholder="Enter element name..."]');
      
      await page.fill('input[placeholder="Enter element name..."]', 'Extraction Comparison Test');
      await page.click('text=Save Element');
      
      await page.waitForSelector('text=Configure Element', { timeout: 5000 });
      await page.click('text=View Dashboard');
      await page.waitForSelector('[data-testid="validation-modal"]');
      
      const elementCard = page.locator('.grid').locator('.hover\\:shadow-md').first();
      await elementCard.locator('text=Test').click();
      await page.waitForSelector('text=Upload Files');
      
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles('test.txt');
      await page.waitForSelector('text=test.txt');
      
      await page.click('text=Run Analysis');
      await page.waitForSelector('text=AI Analysis Results', { timeout: 90000 });
      
      const resultsSection = page.locator('text=AI Analysis Results').locator('..');
      extractionResult = await resultsSection.textContent() || '';
      await page.keyboard.press('Escape'); // Close processing modal
      await page.keyboard.press('Escape'); // Close dashboard
    }
    
    // Test reasoning method
    {
      await page.click('text=Configure Element');
      await page.waitForSelector('text=Select AI Model');
      
      await page.fill('textarea[placeholder="Enter your prompt here..."]', 'How many complaints are for Israel?');
      
      await page.locator('text=Select Method').click();
      await page.click('text=Reasoning');
      
      await page.locator('text=Select AI Model').click();
      await page.click('text=GPT-4');
      
      await page.locator('text=Select File Type').click();
      await page.click('text=TXT');
      
      await page.click('text=Next');
      await page.waitForSelector('input[placeholder="Enter element name..."]');
      
      await page.fill('input[placeholder="Enter element name..."]', 'Reasoning Comparison Test');
      await page.click('text=Save Element');
      
      await page.waitForSelector('text=Configure Element', { timeout: 5000 });
      await page.click('text=View Dashboard');
      await page.waitForSelector('[data-testid="validation-modal"]');
      
      const elementCard = page.locator('.grid').locator('.hover\\:shadow-md').first();
      await elementCard.locator('text=Test').click();
      await page.waitForSelector('text=Upload Files');
      
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles('test.txt');
      await page.waitForSelector('text=test.txt');
      
      await page.click('text=Run Analysis');
      await page.waitForSelector('text=AI Analysis Results', { timeout: 90000 });
      
      const resultsSection = page.locator('text=AI Analysis Results').locator('..');
      reasoningResult = await resultsSection.textContent() || '';
      await page.keyboard.press('Escape'); // Close processing modal
      await page.keyboard.press('Escape'); // Close dashboard
    }
    
    // Compare results
    console.log('📊 EXTRACTION RESULT:', extractionResult);
    console.log('📊 REASONING RESULT:', reasoningResult);
    
    // Both should identify Israel-related content
    expect(extractionResult.toLowerCase()).toContain('israel');
    expect(reasoningResult.toLowerCase()).toContain('israel');
    
    // Extraction should provide more specific listing
    const extractionHasDetailedList = extractionResult.includes('000201357115') || extractionResult.includes('QE-004535');
    const reasoningProvidesAnalysis = reasoningResult.length > extractionResult.length * 0.5;
    
    console.log('✅ Both methods successfully processed the same data with different approaches');
    console.log('📋 Extraction method provides detailed listing:', extractionHasDetailedList);
    console.log('📋 Reasoning method provides analytical response:', reasoningProvidesAnalysis);
  });

  test('Element Validation and Dataset Integration Flow', async ({ page }) => {
    console.log('🧪 Testing Element Validation and Dataset Integration');
    
    // Create element
    await page.click('text=Configure Element');
    await page.waitForSelector('text=Select AI Model');
    
    await page.fill('textarea[placeholder="Enter your prompt here..."]', 'Test prompt for validation');
    
    await page.locator('text=Select Method').click();
    await page.click('text=Extraction');
    
    await page.locator('text=Select AI Model').click();
    await page.click('text=GPT-4');
    
    await page.locator('text=Select File Type').click();
    await page.click('text=TXT');
    
    await page.click('text=Next');
    await page.waitForSelector('input[placeholder="Enter element name..."]');
    
    await page.fill('input[placeholder="Enter element name..."]', 'Validation Test Element');
    await page.click('text=Save Element');
    
    // Wait for save completion and open dashboard
    await page.waitForSelector('text=Configure Element', { timeout: 5000 });
    await page.click('text=View Dashboard');
    await page.waitForSelector('[data-testid="validation-modal"]');
    
    // Test the element by running analysis to validate it
    const elementCard = page.locator('.grid').locator('.hover\\:shadow-md').first();
    await elementCard.locator('text=Test').click();
    await page.waitForSelector('text=Upload Files');
    
    // Upload test.txt file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('test.txt');
    
    // Wait for file to be uploaded and click Run Analysis
    await page.waitForSelector('text=test.txt');
    await page.click('text=Run Analysis');
    
    // Wait for analysis to complete
    await page.waitForSelector('text=AI Analysis Results', { timeout: 90000 });
    
    // Click Validate Element button in processing modal
    await page.click('text=Validate Element');
    
    // Wait for validation to complete and return to dashboard
    await page.waitForSelector('[data-testid="validation-modal"]');
    
    // Check that element is now validated (green badge)
    await expect(elementCard.locator('text=Validated')).toBeVisible();
    await expect(elementCard.locator('.bg-green-500')).toBeVisible();
    
    // Test clicking on validated element to access results directly
    await elementCard.click();
    await page.waitForSelector('text=AI Analysis Results', { timeout: 10000 });
    
    // Click Add to Dataset button in processing modal
    await page.click('text=Add to Dataset');
    
    // Fill dataset entry form
    await page.waitForSelector('textarea');
    const textareas = page.locator('textarea');
    await textareas.nth(0).fill('{"test": "config"}'); // JSON config
    await textareas.nth(1).fill('Test AI output for dataset'); // AI output
    
    await page.click('text=Save to Dataset');
    
    // Wait for success and close
    await page.waitForSelector('text=View Dashboard', { timeout: 5000 });
    
    console.log('✅ Element validation and dataset integration flow completed successfully');
  });
});