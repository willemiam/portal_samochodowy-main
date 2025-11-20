<script lang="ts">
  import { wizardStore } from '../stores/wizardStore';

  let state = $state($wizardStore);

  $effect(() => {
    state = $wizardStore;
  });

  function toggleFeature(feature: string) {
    wizardStore.updateFeatures({ [feature]: !state.platformConfig.features[feature] });
  }
</script>

<div class="step-container">
  <h2>Platform Features</h2>
  <p class="step-description">Select the features you want to enable for your platform</p>

  <div class="features-grid">
    <div class="feature-card">
      <div class="feature-header">
        <input
          type="checkbox"
          id="feature-search"
          checked={state.platformConfig.features.search}
          onchange={() => toggleFeature('search')}
        />
        <label for="feature-search">
          <h3>Search</h3>
        </label>
      </div>
      <p>Enable full-text search across all items</p>
    </div>

    <div class="feature-card">
      <div class="feature-header">
        <input
          type="checkbox"
          id="feature-filters"
          checked={state.platformConfig.features.filters}
          onchange={() => toggleFeature('filters')}
        />
        <label for="feature-filters">
          <h3>Advanced Filters</h3>
        </label>
      </div>
      <p>Allow users to filter items by various criteria</p>
    </div>

    <div class="feature-card">
      <div class="feature-header">
        <input
          type="checkbox"
          id="feature-ai"
          checked={state.platformConfig.features.aiEnhancement}
          onchange={() => toggleFeature('aiEnhancement')}
        />
        <label for="feature-ai">
          <h3>AI Enhancement</h3>
        </label>
      </div>
      <p>Use AI to enhance item descriptions via MCP</p>
    </div>

    <div class="feature-card">
      <div class="feature-header">
        <input
          type="checkbox"
          id="feature-accounts"
          checked={state.platformConfig.features.userAccounts}
          onchange={() => toggleFeature('userAccounts')}
        />
        <label for="feature-accounts">
          <h3>User Accounts</h3>
        </label>
      </div>
      <p>Enable user registration and authentication</p>
    </div>
  </div>
</div>

<style>
  .step-container {
    padding: 2rem;
    max-width: 800px;
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

  .features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
  }

  .feature-card {
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    padding: 1.5rem;
    transition: all 0.3s ease;
  }

  .feature-card:hover {
    border-color: #4CAF50;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .feature-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
  }

  input[type="checkbox"] {
    width: 20px;
    height: 20px;
    cursor: pointer;
  }

  label {
    cursor: pointer;
    margin: 0;
  }

  h3 {
    margin: 0;
    font-size: 1.1rem;
    color: #333;
  }

  p {
    margin: 0;
    color: #666;
    font-size: 0.9rem;
    line-height: 1.4;
  }
</style>
