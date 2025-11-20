<script lang="ts">
  import { wizardStore } from '../stores/wizardStore';

  let features: string[] = [];
  
  const availableFeatures = [
    { id: 'search', label: 'Advanced Search' },
    { id: 'filters', label: 'Dynamic Filters' },
    { id: 'comparison', label: 'Item Comparison' },
    { id: 'recommendations', label: 'AI Recommendations' },
    { id: 'notifications', label: 'Real-time Notifications' },
    { id: 'analytics', label: 'Analytics Dashboard' },
    { id: 'api', label: 'Public API Access' },
    { id: 'mobile', label: 'Mobile App Support' }
  ];

  wizardStore.subscribe(state => {
    features = state.platformData.features || [];
  });

  function toggleFeature(featureId: string) {
    if (features.includes(featureId)) {
      features = features.filter(f => f !== featureId);
    } else {
      features = [...features, featureId];
    }
    wizardStore.updatePlatformData({ features });
  }

  function isSelected(featureId: string): boolean {
    return features.includes(featureId);
  }
</script>

<div class="step-container">
  <h2>Platform Features</h2>
  <p class="step-description">Select the features you want to enable for your platform</p>

  <div class="features-grid">
    {#each availableFeatures as feature}
      <div
        class="feature-card"
        class:selected={isSelected(feature.id)}
        on:click={() => toggleFeature(feature.id)}
        on:keypress={(e) => e.key === 'Enter' && toggleFeature(feature.id)}
        role="button"
        tabindex="0"
      >
        <div class="checkbox">
          {#if isSelected(feature.id)}
            <span class="checkmark">✓</span>
          {/if}
        </div>
        <div class="feature-label">{feature.label}</div>
      </div>
    {/each}
  </div>

  <div class="selected-count">
    {features.length} feature{features.length !== 1 ? 's' : ''} selected
  </div>
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

  .features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .feature-card {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    border: 2px solid #ddd;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    background: white;
  }

  .feature-card:hover {
    border-color: #007bff;
    background: #f8f9fa;
  }

  .feature-card.selected {
    border-color: #007bff;
    background: #e7f3ff;
  }

  .checkbox {
    width: 24px;
    height: 24px;
    border: 2px solid #ddd;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .feature-card.selected .checkbox {
    background: #007bff;
    border-color: #007bff;
  }

  .checkmark {
    color: white;
    font-weight: bold;
    font-size: 1.2rem;
  }

  .feature-label {
    font-weight: 500;
    color: #333;
  }

  .selected-count {
    text-align: center;
    color: #666;
    font-size: 0.9rem;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 4px;
  }
</style>
