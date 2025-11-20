<script lang="ts">
  import { wizardStore } from '../stores/wizardStore';
  import { createPlatform, previewPlatform, type PreviewResponse } from '../api/platform';
  
  let config: any = {};
  let platformId: string = '';
  let isSaving = false;
  let saveError = '';
  let saveSuccess = false;
  
  let isPreviewLoading = false;
  let previewError = '';
  let previewResult: PreviewResponse | null = null;
  
  let previewItemData = JSON.stringify({
    name: 'Sample Car',
    make: 'Toyota',
    model: 'Camry',
    year: 2023,
    price: 25000
  }, null, 2);
  
  wizardStore.subscribe(c => {
    config = c;
  });
  
  async function savePlatform() {
    isSaving = true;
    saveError = '';
    saveSuccess = false;
    
    try {
      const response = await createPlatform(config);
      platformId = response.id;
      saveSuccess = true;
      console.log('Platform saved:', response);
    } catch (error) {
      saveError = error instanceof Error ? error.message : 'Failed to save platform';
      console.error('Save error:', error);
    } finally {
      isSaving = false;
    }
  }
  
  async function generatePreview() {
    if (!platformId) {
      previewError = 'Please save the platform first';
      return;
    }
    
    isPreviewLoading = true;
    previewError = '';
    previewResult = null;
    
    try {
      let itemData = {};
      try {
        itemData = JSON.parse(previewItemData);
      } catch (e) {
        throw new Error('Invalid JSON in item data');
      }
      
      const response = await previewPlatform(platformId, {
        domain: config.domain,
        item_data: itemData
      });
      
      previewResult = response;
      console.log('Preview generated:', response);
    } catch (error) {
      previewError = error instanceof Error ? error.message : 'Failed to generate preview';
      console.error('Preview error:', error);
    } finally {
      isPreviewLoading = false;
    }
  }
</script>

<div class="step-container">
  <h2>Summary & Preview</h2>
  <p>Review your platform configuration and test the preview</p>
  
  <div class="summary-section">
    <h3>Configuration Summary</h3>
    <div class="config-display">
      <div class="config-item">
        <strong>Name:</strong> {config.name || 'N/A'}
      </div>
      <div class="config-item">
        <strong>Description:</strong> {config.description || 'N/A'}
      </div>
      <div class="config-item">
        <strong>Domain:</strong> {config.domain || 'N/A'}
      </div>
      <div class="config-item">
        <strong>Features:</strong> {config.features?.length || 0} selected
      </div>
      <div class="config-item">
        <strong>Theme:</strong> {config.advanced?.theme || 'light'}
      </div>
      <div class="config-item">
        <strong>Language:</strong> {config.advanced?.language || 'en'}
      </div>
    </div>
  </div>
  
  <div class="actions-section">
    <button 
      class="btn btn-primary" 
      on:click={savePlatform}
      disabled={isSaving}
    >
      {isSaving ? 'Saving...' : 'Save Platform'}
    </button>
    
    {#if saveError}
      <div class="alert alert-error">{saveError}</div>
    {/if}
    
    {#if saveSuccess}
      <div class="alert alert-success">
        Platform saved successfully! ID: {platformId}
      </div>
    {/if}
  </div>
  
  {#if platformId}
    <div class="preview-section">
      <h3>Test Preview</h3>
      <p class="section-description">
        Test the mock MCP preview functionality with sample data
      </p>
      
      <div class="form-group">
        <label for="previewData">Item Data (JSON)</label>
        <textarea 
          id="previewData"
          bind:value={previewItemData}
          rows="8"
        ></textarea>
      </div>
      
      <button 
        class="btn btn-secondary" 
        on:click={generatePreview}
        disabled={isPreviewLoading}
      >
        {isPreviewLoading ? 'Generating...' : 'Generate Preview'}
      </button>
      
      {#if previewError}
        <div class="alert alert-error">{previewError}</div>
      {/if}
      
      {#if previewResult}
        <div class="preview-result">
          <h4>Preview Result:</h4>
          <div class="result-box">
            <strong>Enhanced Text:</strong>
            <p>{previewResult.enhanced_text}</p>
          </div>
          <div class="result-meta">
            <small>Session ID: {previewResult.session_id}</small>
          </div>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .step-container {
    max-width: 700px;
    margin: 0 auto;
    padding: 20px;
  }
  
  h2 {
    margin-bottom: 10px;
    color: #333;
  }
  
  h3 {
    margin-bottom: 15px;
    color: #444;
    font-size: 1.2em;
  }
  
  h4 {
    margin-bottom: 10px;
    color: #555;
  }
  
  p {
    color: #666;
    margin-bottom: 20px;
  }
  
  .section-description {
    font-size: 14px;
    margin-bottom: 15px;
  }
  
  .summary-section {
    background-color: #f9f9f9;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 30px;
  }
  
  .config-display {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
  }
  
  .config-item {
    color: #333;
  }
  
  .config-item strong {
    display: block;
    margin-bottom: 5px;
    color: #666;
    font-size: 12px;
  }
  
  .actions-section {
    margin-bottom: 30px;
  }
  
  .preview-section {
    border-top: 2px solid #eee;
    padding-top: 30px;
    margin-top: 30px;
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: #333;
  }
  
  textarea {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    font-family: 'Courier New', monospace;
    resize: vertical;
  }
  
  textarea:focus {
    outline: none;
    border-color: #4CAF50;
  }
  
  .btn {
    padding: 12px 24px;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .btn-primary {
    background-color: #4CAF50;
    color: white;
  }
  
  .btn-primary:hover:not(:disabled) {
    background-color: #45a049;
  }
  
  .btn-secondary {
    background-color: #2196F3;
    color: white;
  }
  
  .btn-secondary:hover:not(:disabled) {
    background-color: #0b7dda;
  }
  
  .alert {
    margin-top: 15px;
    padding: 12px;
    border-radius: 4px;
  }
  
  .alert-error {
    background-color: #ffebee;
    color: #c62828;
    border: 1px solid #ef5350;
  }
  
  .alert-success {
    background-color: #e8f5e9;
    color: #2e7d32;
    border: 1px solid #66bb6a;
  }
  
  .preview-result {
    margin-top: 20px;
    padding: 20px;
    background-color: #f5f5f5;
    border-radius: 8px;
  }
  
  .result-box {
    background-color: white;
    padding: 15px;
    border-radius: 4px;
    margin-bottom: 10px;
  }
  
  .result-box p {
    margin-top: 10px;
    color: #333;
    line-height: 1.6;
  }
  
  .result-meta {
    color: #999;
    font-size: 12px;
  }
</style>
