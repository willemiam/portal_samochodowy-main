<script lang="ts">
  import { wizardStore } from '../stores/wizardStore';
  
  let name = '';
  let description = '';
  let domain = '';
  
  // Load current values
  wizardStore.subscribe(config => {
    name = config.name;
    description = config.description;
    domain = config.domain;
  });
  
  function updateStore() {
    wizardStore.update(config => ({
      ...config,
      name,
      description,
      domain
    }));
  }
</script>

<div class="step-container">
  <h2>Basic Information</h2>
  <p>Provide basic information about your platform</p>
  
  <div class="form-group">
    <label for="name">Platform Name *</label>
    <input 
      id="name"
      type="text" 
      bind:value={name}
      on:blur={updateStore}
      placeholder="e.g., Car Sales Platform"
      required
    />
  </div>
  
  <div class="form-group">
    <label for="description">Description *</label>
    <textarea 
      id="description"
      bind:value={description}
      on:blur={updateStore}
      placeholder="Describe your platform's purpose..."
      rows="4"
      required
    ></textarea>
  </div>
  
  <div class="form-group">
    <label for="domain">Domain *</label>
    <input 
      id="domain"
      type="text" 
      bind:value={domain}
      on:blur={updateStore}
      placeholder="e.g., automotive, real-estate"
      required
    />
  </div>
</div>

<style>
  .step-container {
    max-width: 600px;
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
  
  .form-group {
    margin-bottom: 20px;
  }
  
  label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: #333;
  }
  
  input, textarea {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    font-family: inherit;
  }
  
  input:focus, textarea:focus {
    outline: none;
    border-color: #4CAF50;
  }
  
  textarea {
    resize: vertical;
  }
</style>
