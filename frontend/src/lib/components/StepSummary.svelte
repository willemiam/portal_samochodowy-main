<script lang="ts">
  import { wizardStore } from '../stores/wizardStore';
  import { createPlatform, createPreview, type PreviewResponse } from '../api/platform';

  let platformData: any = {};
  let isLoading = false;
  let error: string | null = null;
  let platformId: string | null = null;
  let preview: PreviewResponse | null = null;

  wizardStore.subscribe(state => {
    platformData = state.platformData;
    isLoading = state.isLoading;
    error = state.error;
  });

  async function handleSave() {
    wizardStore.setLoading(true);
    wizardStore.setError(null);
    error = null;
    
    try {
      const response = await createPlatform(platformData);
      platformId = response.id;
      wizardStore.updatePlatformData({ id: response.id, created_at: response.created_at });
      alert(`Platform saved successfully! ID: ${response.id}`);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to save platform';
      error = errorMsg;
      wizardStore.setError(errorMsg);
    } finally {
      wizardStore.setLoading(false);
    }
  }

  async function handlePreview() {
    if (!platformId) {
      alert('Please save the platform first before generating a preview.');
      return;
    }
    
    wizardStore.setLoading(true);
    wizardStore.setError(null);
    error = null;
    preview = null;
    
    try {
      preview = await createPreview(platformId);
      alert('Preview generated successfully!');
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to generate preview';
      error = errorMsg;
      wizardStore.setError(errorMsg);
    } finally {
      wizardStore.setLoading(false);
    }
  }

  function handleReset() {
    if (confirm('Are you sure you want to reset the wizard? All data will be lost.')) {
      wizardStore.reset();
      platformId = null;
      preview = null;
      error = null;
    }
  }
</script>

<div class="step-container">
  <h2>Summary & Preview</h2>
  <p class="step-description">Review your configuration and save the platform</p>

  {#if error}
    <div class="alert alert-error">
      {error}
    </div>
  {/if}

  <div class="summary-section">
    <h3>Basic Information</h3>
    <div class="summary-item">
      <span class="label">Name:</span>
      <span class="value">{platformData.name || 'Not set'}</span>
    </div>
    <div class="summary-item">
      <span class="label">Domain:</span>
      <span class="value">{platformData.domain || 'Not set'}</span>
    </div>
    <div class="summary-item">
      <span class="label">Description:</span>
      <span class="value">{platformData.description || 'Not set'}</span>
    </div>
  </div>

  <div class="summary-section">
    <h3>Features</h3>
    <div class="summary-item">
      {#if platformData.features && platformData.features.length > 0}
        <ul>
          {#each platformData.features as feature}
            <li>{feature}</li>
          {/each}
        </ul>
      {:else}
        <span class="value">No features selected</span>
      {/if}
    </div>
  </div>

  <div class="summary-section">
    <h3>Domain Details</h3>
    <div class="summary-item">
      <span class="label">Target Audience:</span>
      <span class="value">{platformData.targetAudience || 'Not set'}</span>
    </div>
    <div class="summary-item">
      <span class="label">Primary Goals:</span>
      {#if platformData.primaryGoals && platformData.primaryGoals.length > 0}
        <ul>
          {#each platformData.primaryGoals as goal}
            <li>{goal}</li>
          {/each}
        </ul>
      {:else}
        <span class="value">No goals selected</span>
      {/if}
    </div>
  </div>

  {#if platformData.customSettings && Object.keys(platformData.customSettings).length > 0}
    <div class="summary-section">
      <h3>Advanced Settings</h3>
      {#each Object.entries(platformData.customSettings) as [key, value]}
        <div class="summary-item">
          <span class="label">{key}:</span>
          <span class="value">{value}</span>
        </div>
      {/each}
    </div>
  {/if}

  <div class="action-buttons">
    <button class="btn btn-primary" on:click={handleSave} disabled={isLoading}>
      {isLoading ? 'Saving...' : 'Save Platform'}
    </button>
    
    <button class="btn btn-secondary" on:click={handlePreview} disabled={isLoading || !platformId}>
      {isLoading ? 'Generating...' : 'Generate Preview'}
    </button>
    
    <button class="btn btn-danger" on:click={handleReset}>
      Reset Wizard
    </button>
  </div>

  {#if platformId}
    <div class="platform-id-display">
      <strong>Platform ID:</strong> {platformId}
    </div>
  {/if}

  {#if preview}
    <div class="preview-section">
      <h3>Preview Result</h3>
      <div class="preview-content">
        <div class="preview-meta">
          <div><strong>Preview ID:</strong> {preview.id}</div>
          <div><strong>Session ID:</strong> {preview.session_id}</div>
          <div><strong>Created:</strong> {new Date(preview.created_at).toLocaleString()}</div>
        </div>
        <div class="preview-text">
          <h4>Enhanced Text:</h4>
          <div class="enhanced-text">{@html preview.enhanced_text.replace(/\n/g, '<br>')}</div>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .step-container {
    max-width: 700px;
  }

  h2 {
    color: #333;
    margin-bottom: 0.5rem;
  }

  .step-description {
    color: #666;
    margin-bottom: 2rem;
  }

  .alert {
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1.5rem;
  }

  .alert-error {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
  }

  .summary-section {
    margin-bottom: 2rem;
    padding: 1.5rem;
    background: #f8f9fa;
    border-radius: 4px;
  }

  h3 {
    color: #333;
    margin-bottom: 1rem;
    font-size: 1.1rem;
  }

  .summary-item {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
  }

  .label {
    font-weight: 600;
    color: #333;
    min-width: 150px;
  }

  .value {
    color: #666;
    flex: 1;
  }

  ul {
    margin: 0;
    padding-left: 1.5rem;
    color: #666;
  }

  li {
    margin-bottom: 0.25rem;
  }

  .action-buttons {
    display: flex;
    gap: 1rem;
    margin-top: 2rem;
    flex-wrap: wrap;
  }

  .btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.2s;
    font-weight: 500;
  }

  .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-primary {
    background: #007bff;
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    background: #0056b3;
  }

  .btn-secondary {
    background: #6c757d;
    color: white;
  }

  .btn-secondary:hover:not(:disabled) {
    background: #545b62;
  }

  .btn-danger {
    background: #dc3545;
    color: white;
  }

  .btn-danger:hover {
    background: #c82333;
  }

  .platform-id-display {
    margin-top: 1.5rem;
    padding: 1rem;
    background: #d4edda;
    border: 1px solid #c3e6cb;
    border-radius: 4px;
    color: #155724;
  }

  .preview-section {
    margin-top: 2rem;
    padding: 1.5rem;
    background: white;
    border: 2px solid #007bff;
    border-radius: 4px;
  }

  .preview-content {
    margin-top: 1rem;
  }

  .preview-meta {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 4px;
    margin-bottom: 1rem;
    font-size: 0.9rem;
  }

  .preview-text {
    margin-top: 1rem;
  }

  h4 {
    color: #333;
    margin-bottom: 0.75rem;
  }

  .enhanced-text {
    padding: 1rem;
    background: #f8f9fa;
    border-left: 4px solid #007bff;
    border-radius: 4px;
    line-height: 1.6;
    white-space: pre-wrap;
    color: #333;
  }
</style>
