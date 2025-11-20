<script lang="ts">
  import { wizardStore } from '../stores/wizardStore';
  
  const availableFeatures = [
    { id: 'search', label: 'Advanced Search' },
    { id: 'filters', label: 'Filtering' },
    { id: 'ai-descriptions', label: 'AI-Enhanced Descriptions' },
    { id: 'user-auth', label: 'User Authentication' },
    { id: 'image-upload', label: 'Image Upload' },
    { id: 'notifications', label: 'Notifications' },
    { id: 'analytics', label: 'Analytics' },
  ];
  
  let selectedFeatures: string[] = [];
  
  // Load current values
  wizardStore.subscribe(config => {
    selectedFeatures = config.features || [];
  });
  
  function toggleFeature(featureId: string) {
    if (selectedFeatures.includes(featureId)) {
      selectedFeatures = selectedFeatures.filter(f => f !== featureId);
    } else {
      selectedFeatures = [...selectedFeatures, featureId];
    }
    
    wizardStore.update(config => ({
      ...config,
      features: selectedFeatures
    }));
  }
</script>

<div class="step-container">
  <h2>Platform Features</h2>
  <p>Select the features you want to enable for your platform</p>
  
  <div class="features-grid">
    {#each availableFeatures as feature}
      <div class="feature-card" class:selected={selectedFeatures.includes(feature.id)}>
        <label>
          <input 
            type="checkbox" 
            checked={selectedFeatures.includes(feature.id)}
            on:change={() => toggleFeature(feature.id)}
          />
          <span>{feature.label}</span>
        </label>
      </div>
    {/each}
  </div>
  
  <div class="selected-count">
    {selectedFeatures.length} feature{selectedFeatures.length !== 1 ? 's' : ''} selected
  </div>
</div>

<style>
  .step-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
  }
  
  h2 {
    margin-bottom: 10px;
    color: #333;
  }
  
  p {
    color: #666;
    margin-bottom: 30px;
  }
  
  .features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 15px;
    margin-bottom: 20px;
  }
  
  .feature-card {
    border: 2px solid #ddd;
    border-radius: 8px;
    padding: 15px;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .feature-card:hover {
    border-color: #4CAF50;
    background-color: #f9f9f9;
  }
  
  .feature-card.selected {
    border-color: #4CAF50;
    background-color: #e8f5e9;
  }
  
  .feature-card label {
    display: flex;
    align-items: center;
    cursor: pointer;
    margin: 0;
  }
  
  .feature-card input[type="checkbox"] {
    margin-right: 10px;
    cursor: pointer;
  }
  
  .feature-card span {
    color: #333;
    font-weight: 500;
  }
  
  .selected-count {
    text-align: center;
    color: #666;
    font-style: italic;
  }
</style>
