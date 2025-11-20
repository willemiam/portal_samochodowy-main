<script lang="ts">
  import { wizardStore } from '../stores/wizardStore';
  import { previewPlatform } from '../lib/api/platform';

  let state = $state($wizardStore);
  let previewData = $state({
    domain: '',
    item_data: {} as Record<string, any>
  });
  let previewResult = $state<any>(null);
  let isLoadingPreview = $state(false);
  let previewError = $state<string | null>(null);

  $effect(() => {
    state = $wizardStore;
    // Initialize preview data with platform config
    previewData.domain = state.platformConfig.domain;
    
    // Create sample item data based on primary fields
    const sampleData: Record<string, any> = {};
    state.platformConfig.domainDetails.primaryFields.forEach((field, index) => {
      sampleData[field] = `Sample ${field} value ${index + 1}`;
    });
    previewData.item_data = sampleData;
  });

  async function handlePreview() {
    if (!state.platformId) {
      previewError = 'Platform must be saved before preview';
      return;
    }

    isLoadingPreview = true;
    previewError = null;

    try {
      const result = await previewPlatform(state.platformId, previewData);
      previewResult = result;
    } catch (error) {
      previewError = error instanceof Error ? error.message : 'Failed to generate preview';
      console.error('Preview error:', error);
    } finally {
      isLoadingPreview = false;
    }
  }
</script>

<div class="step-container">
  <h2>Summary & Review</h2>
  <p class="step-description">Review your platform configuration before saving</p>

  <div class="summary-section">
    <h3>Basic Information</h3>
    <div class="summary-item">
      <strong>Platform Name:</strong>
      <span>{state.platformConfig.name || 'Not set'}</span>
    </div>
    <div class="summary-item">
      <strong>Description:</strong>
      <span>{state.platformConfig.description || 'Not set'}</span>
    </div>
    <div class="summary-item">
      <strong>Domain:</strong>
      <span>{state.platformConfig.domain || 'Not set'}</span>
    </div>
  </div>

  <div class="summary-section">
    <h3>Features</h3>
    <div class="features-list">
      <div class="feature-item">
        <input type="checkbox" checked={state.platformConfig.features.search} disabled />
        <span>Search</span>
      </div>
      <div class="feature-item">
        <input type="checkbox" checked={state.platformConfig.features.filters} disabled />
        <span>Advanced Filters</span>
      </div>
      <div class="feature-item">
        <input type="checkbox" checked={state.platformConfig.features.aiEnhancement} disabled />
        <span>AI Enhancement</span>
      </div>
      <div class="feature-item">
        <input type="checkbox" checked={state.platformConfig.features.userAccounts} disabled />
        <span>User Accounts</span>
      </div>
    </div>
  </div>

  <div class="summary-section">
    <h3>Domain Details</h3>
    <div class="summary-item">
      <strong>Item Name:</strong>
      <span>{state.platformConfig.domainDetails.itemName || 'Not set'} / {state.platformConfig.domainDetails.itemNamePlural || 'Not set'}</span>
    </div>
    <div class="summary-item">
      <strong>Primary Fields:</strong>
      <span>
        {#if state.platformConfig.domainDetails.primaryFields.length > 0}
          {state.platformConfig.domainDetails.primaryFields.join(', ')}
        {:else}
          None
        {/if}
      </span>
    </div>
  </div>

  {#if state.platformConfig.features.aiEnhancement}
    <div class="summary-section">
      <h3>Advanced Settings</h3>
      <div class="summary-item">
        <strong>MCP Endpoint:</strong>
        <span>{state.platformConfig.advanced.mcpEndpoint || 'Not configured (will use mock)'}</span>
      </div>
    </div>
  {/if}

  {#if state.platformId}
    <div class="preview-section">
      <h3>Test Preview</h3>
      <p>Test the AI enhancement feature with sample data</p>
      
      <button 
        type="button" 
        onclick={handlePreview}
        disabled={isLoadingPreview}
        class="preview-btn"
      >
        {isLoadingPreview ? 'Generating Preview...' : 'Generate Preview'}
      </button>

      {#if previewError}
        <div class="error-message">{previewError}</div>
      {/if}

      {#if previewResult}
        <div class="preview-result">
          <h4>Preview Result:</h4>
          <div class="enhanced-text">
            <strong>Enhanced Text:</strong>
            <p>{previewResult.enhanced_text}</p>
          </div>
          <div class="preview-meta">
            <small>Session ID: {previewResult.session_id}</small>
            <small>Created: {new Date(previewResult.created_at).toLocaleString()}</small>
          </div>
        </div>
      {/if}
    </div>
  {:else}
    <div class="info-box">
      <strong>Note:</strong> Save your platform configuration to enable preview functionality.
    </div>
  {/if}
</div>

<style>
  .step-container {
    padding: 2rem;
    max-width: 700px;
    margin: 0 auto;
  }

  h2 {
    margin-bottom: 0.5rem;
    color: #333;
  }

  .step-description {
    color: #666;
    margin-bottom: 2rem;
  }

  .summary-section {
    background-color: #f9f9f9;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }

  h3 {
    margin: 0 0 1rem 0;
    color: #333;
    font-size: 1.1rem;
    border-bottom: 2px solid #4CAF50;
    padding-bottom: 0.5rem;
  }

  .summary-item {
    display: flex;
    gap: 1rem;
    margin-bottom: 0.75rem;
  }

  .summary-item strong {
    min-width: 150px;
    color: #555;
  }

  .summary-item span {
    color: #333;
    flex: 1;
  }

  .features-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 0.75rem;
  }

  .feature-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .feature-item input[type="checkbox"] {
    cursor: default;
  }

  .preview-section {
    background-color: #e8f5e9;
    border: 1px solid #4CAF50;
    border-radius: 8px;
    padding: 1.5rem;
    margin-top: 2rem;
  }

  .preview-section h3 {
    border-bottom-color: #2e7d32;
  }

  .preview-btn {
    padding: 0.75rem 1.5rem;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
    font-size: 1rem;
    transition: background-color 0.2s;
    margin-top: 1rem;
  }

  .preview-btn:hover:not(:disabled) {
    background-color: #45a049;
  }

  .preview-btn:disabled {
    background-color: #9e9e9e;
    cursor: not-allowed;
  }

  .preview-result {
    margin-top: 1.5rem;
    padding: 1rem;
    background-color: white;
    border-radius: 4px;
  }

  h4 {
    margin: 0 0 1rem 0;
    color: #333;
  }

  .enhanced-text {
    margin-bottom: 1rem;
  }

  .enhanced-text strong {
    display: block;
    margin-bottom: 0.5rem;
    color: #555;
  }

  .enhanced-text p {
    margin: 0;
    padding: 1rem;
    background-color: #f5f5f5;
    border-left: 3px solid #4CAF50;
    border-radius: 4px;
  }

  .preview-meta {
    display: flex;
    gap: 1rem;
    padding-top: 0.5rem;
    border-top: 1px solid #e0e0e0;
  }

  .preview-meta small {
    color: #666;
  }

  .error-message {
    margin-top: 1rem;
    padding: 1rem;
    background-color: #ffebee;
    border-left: 4px solid #f44336;
    color: #c62828;
    border-radius: 4px;
  }

  .info-box {
    background-color: #e3f2fd;
    border-left: 4px solid #2196F3;
    padding: 1rem;
    border-radius: 4px;
    margin-top: 2rem;
  }

  .info-box strong {
    color: #1976D2;
  }
</style>
