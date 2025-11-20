<script lang="ts">
  import { wizardStore } from '../stores/wizardStore';

  let name = '';
  let description = '';
  let domain = '';

  wizardStore.subscribe(state => {
    name = state.platformData.name;
    description = state.platformData.description;
    domain = state.platformData.domain;
  });

  function handleUpdate() {
    wizardStore.updatePlatformData({ name, description, domain });
  }
</script>

<div class="step-container">
  <h2>Basic Information</h2>
  <p class="step-description">Enter the basic details for your platform</p>

  <div class="form-group">
    <label for="name">Platform Name *</label>
    <input
      id="name"
      type="text"
      bind:value={name}
      on:blur={handleUpdate}
      placeholder="e.g., My Automotive Platform"
      required
    />
  </div>

  <div class="form-group">
    <label for="description">Description *</label>
    <textarea
      id="description"
      bind:value={description}
      on:blur={handleUpdate}
      placeholder="Brief description of your platform's purpose..."
      rows="4"
      required
    ></textarea>
  </div>

  <div class="form-group">
    <label for="domain">Domain *</label>
    <select id="domain" bind:value={domain} on:change={handleUpdate} required>
      <option value="">Select a domain</option>
      <option value="automotive">Automotive</option>
      <option value="ecommerce">E-commerce</option>
      <option value="healthcare">Healthcare</option>
      <option value="education">Education</option>
      <option value="finance">Finance</option>
      <option value="general">General Purpose</option>
    </select>
  </div>
</div>

<style>
  .step-container {
    max-width: 600px;
  }

  h2 {
    color: #333;
    margin-bottom: 0.5rem;
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
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: #333;
  }

  input,
  textarea,
  select {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    font-family: inherit;
  }

  input:focus,
  textarea:focus,
  select:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
  }

  textarea {
    resize: vertical;
  }
</style>
