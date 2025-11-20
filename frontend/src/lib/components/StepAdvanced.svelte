<script lang="ts">
  import { wizardStore } from '../stores/wizardStore';

  let state = $state($wizardStore);

  $effect(() => {
    state = $wizardStore;
  });

  function handleAdvancedInput(field: string, value: string) {
    wizardStore.updateAdvanced({ [field]: value });
  }
</script>

<div class="step-container">
  <h2>Advanced Settings</h2>
  <p class="step-description">Configure advanced options for AI enhancement (optional)</p>

  <div class="form-group">
    <label for="mcp-endpoint">MCP Endpoint URL</label>
    <input
      id="mcp-endpoint"
      type="url"
      placeholder="https://api.example.com/mcp"
      value={state.platformConfig.advanced.mcpEndpoint}
      oninput={(e) => handleAdvancedInput('mcpEndpoint', e.currentTarget.value)}
    />
    <small>The Model Context Protocol endpoint for AI enhancement</small>
  </div>

  <div class="form-group">
    <label for="api-key">API Key</label>
    <input
      id="api-key"
      type="password"
      placeholder="Enter your API key"
      value={state.platformConfig.advanced.apiKey}
      oninput={(e) => handleAdvancedInput('apiKey', e.currentTarget.value)}
    />
    <small>Authentication key for the MCP service</small>
  </div>

  <div class="form-group">
    <label for="custom-prompt">Custom Prompt Template</label>
    <textarea
      id="custom-prompt"
      placeholder="Enter a custom prompt template for AI enhancement (optional)"
      value={state.platformConfig.advanced.customPrompt}
      oninput={(e) => handleAdvancedInput('customPrompt', e.currentTarget.value)}
      rows="6"
    ></textarea>
    <small>
      Customize how AI processes your items. Use placeholders like {'{'}domain{'}'}, {'{'}item_data{'}'}
    </small>
  </div>

  <div class="info-box">
    <strong>Note:</strong> These settings are optional. If not configured, the platform will use
    default mock responses for AI enhancement during development.
  </div>
</div>

<style>
  .step-container {
    padding: 2rem;
    max-width: 600px;
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

  .form-group {
    margin-bottom: 1.5rem;
  }

  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #333;
  }

  input,
  textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    font-family: inherit;
  }

  input:focus,
  textarea:focus {
    outline: none;
    border-color: #4CAF50;
    box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
  }

  small {
    display: block;
    margin-top: 0.25rem;
    color: #666;
    font-size: 0.875rem;
  }

  textarea {
    resize: vertical;
    font-family: 'Courier New', monospace;
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
