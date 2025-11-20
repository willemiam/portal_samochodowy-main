<script lang="ts">
  import { wizardStore } from '../stores/wizardStore';

  let state = $state($wizardStore);
  let newField = $state('');

  $effect(() => {
    state = $wizardStore;
  });

  function handleDetailInput(field: string, value: string) {
    wizardStore.updateDomainDetails({ [field]: value });
  }

  function addPrimaryField() {
    if (newField.trim() && !state.platformConfig.domainDetails.primaryFields.includes(newField.trim())) {
      const updatedFields = [...state.platformConfig.domainDetails.primaryFields, newField.trim()];
      wizardStore.updateDomainDetails({ primaryFields: updatedFields });
      newField = '';
    }
  }

  function removeField(field: string) {
    const updatedFields = state.platformConfig.domainDetails.primaryFields.filter(f => f !== field);
    wizardStore.updateDomainDetails({ primaryFields: updatedFields });
  }

  function handleKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      event.preventDefault();
      addPrimaryField();
    }
  }
</script>

<div class="step-container">
  <h2>Domain Details</h2>
  <p class="step-description">Define the structure and terminology for your domain</p>

  <div class="form-group">
    <label for="item-name">Item Name (Singular) *</label>
    <input
      id="item-name"
      type="text"
      placeholder="e.g., Car, Property, Product"
      value={state.platformConfig.domainDetails.itemName}
      oninput={(e) => handleDetailInput('itemName', e.currentTarget.value)}
      required
    />
    <small>What do you call a single item in your domain?</small>
  </div>

  <div class="form-group">
    <label for="item-name-plural">Item Name (Plural) *</label>
    <input
      id="item-name-plural"
      type="text"
      placeholder="e.g., Cars, Properties, Products"
      value={state.platformConfig.domainDetails.itemNamePlural}
      oninput={(e) => handleDetailInput('itemNamePlural', e.currentTarget.value)}
      required
    />
  </div>

  <div class="form-group">
    <label for="primary-fields">Primary Fields</label>
    <div class="field-input-container">
      <input
        id="primary-fields"
        type="text"
        placeholder="Add a field (e.g., make, model, year)"
        bind:value={newField}
        onkeypress={handleKeyPress}
      />
      <button type="button" onclick={addPrimaryField} class="add-btn">Add</button>
    </div>
    <small>Key attributes that define items in your domain</small>

    {#if state.platformConfig.domainDetails.primaryFields.length > 0}
      <div class="fields-list">
        {#each state.platformConfig.domainDetails.primaryFields as field}
          <div class="field-tag">
            <span>{field}</span>
            <button type="button" onclick={() => removeField(field)} class="remove-btn">×</button>
          </div>
        {/each}
      </div>
    {/if}
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

  input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    font-family: inherit;
  }

  input:focus {
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

  .field-input-container {
    display: flex;
    gap: 0.5rem;
  }

  .field-input-container input {
    flex: 1;
  }

  .add-btn {
    padding: 0.75rem 1.5rem;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
    transition: background-color 0.2s;
  }

  .add-btn:hover {
    background-color: #45a049;
  }

  .fields-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 1rem;
  }

  .field-tag {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background-color: #e8f5e9;
    padding: 0.5rem 0.75rem;
    border-radius: 20px;
    font-size: 0.9rem;
  }

  .remove-btn {
    background: none;
    border: none;
    color: #666;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0;
    line-height: 1;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .remove-btn:hover {
    color: #d32f2f;
  }
</style>
