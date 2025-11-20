<script lang="ts">
  import { wizardStore } from '../stores/wizardStore';

  let state = $state($wizardStore);

  $effect(() => {
    state = $wizardStore;
  });

  function handleInput(field: string, value: string) {
    wizardStore.updateConfig({ [field]: value });
  }
</script>

<div class="step-container">
  <h2>Basic Information</h2>
  <p class="step-description">Enter the basic information about your platform</p>

  <div class="form-group">
    <label for="platform-name">Platform Name *</label>
    <input
      id="platform-name"
      type="text"
      placeholder="e.g., Car Marketplace"
      value={state.platformConfig.name}
      oninput={(e) => handleInput('name', e.currentTarget.value)}
      required
    />
  </div>

  <div class="form-group">
    <label for="platform-description">Description</label>
    <textarea
      id="platform-description"
      placeholder="Brief description of your platform"
      value={state.platformConfig.description}
      oninput={(e) => handleInput('description', e.currentTarget.value)}
      rows="4"
    ></textarea>
  </div>

  <div class="form-group">
    <label for="platform-domain">Domain *</label>
    <input
      id="platform-domain"
      type="text"
      placeholder="e.g., automotive, real-estate, electronics"
      value={state.platformConfig.domain}
      oninput={(e) => handleInput('domain', e.currentTarget.value)}
      required
    />
    <small>The domain/category of items your platform will manage</small>
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
  }
</style>
