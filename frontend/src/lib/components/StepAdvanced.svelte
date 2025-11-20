<script lang="ts">
  import { wizardStore } from '../stores/wizardStore';

  let customSettings: Record<string, any> = {};
  let settingKey = '';
  let settingValue = '';

  wizardStore.subscribe(state => {
    customSettings = state.platformData.customSettings || {};
  });

  function addSetting() {
    if (settingKey && settingValue) {
      customSettings = {
        ...customSettings,
        [settingKey]: settingValue
      };
      wizardStore.updatePlatformData({ customSettings });
      settingKey = '';
      settingValue = '';
    }
  }

  function removeSetting(key: string) {
    const { [key]: removed, ...rest } = customSettings;
    customSettings = rest;
    wizardStore.updatePlatformData({ customSettings });
  }

  function handleKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      event.preventDefault();
      addSetting();
    }
  }
</script>

<div class="step-container">
  <h2>Advanced Settings</h2>
  <p class="step-description">Add custom configuration settings for your platform (optional)</p>

  <div class="settings-input">
    <div class="input-row">
      <input
        type="text"
        bind:value={settingKey}
        placeholder="Setting name (e.g., max_results)"
        on:keypress={handleKeyPress}
      />
      <input
        type="text"
        bind:value={settingValue}
        placeholder="Value (e.g., 100)"
        on:keypress={handleKeyPress}
      />
      <button class="btn-add" on:click={addSetting}>Add</button>
    </div>
  </div>

  {#if Object.keys(customSettings).length > 0}
    <div class="settings-list">
      <h3>Current Settings</h3>
      <div class="settings-items">
        {#each Object.entries(customSettings) as [key, value]}
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-key">{key}</span>
              <span class="setting-value">{value}</span>
            </div>
            <button class="btn-remove" on:click={() => removeSetting(key)}>×</button>
          </div>
        {/each}
      </div>
    </div>
  {:else}
    <div class="empty-state">
      <p>No custom settings added yet. This step is optional.</p>
    </div>
  {/if}
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

  .settings-input {
    margin-bottom: 2rem;
  }

  .input-row {
    display: flex;
    gap: 0.5rem;
  }

  .input-row input {
    flex: 1;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
  }

  .input-row input:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
  }

  .btn-add {
    padding: 0.75rem 1.5rem;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
    transition: background 0.2s;
  }

  .btn-add:hover {
    background: #0056b3;
  }

  .settings-list {
    margin-top: 2rem;
  }

  h3 {
    color: #333;
    margin-bottom: 1rem;
    font-size: 1.1rem;
  }

  .settings-items {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .setting-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    background: #f8f9fa;
    border: 1px solid #ddd;
    border-radius: 4px;
  }

  .setting-info {
    display: flex;
    gap: 1rem;
    flex: 1;
  }

  .setting-key {
    font-weight: 600;
    color: #333;
  }

  .setting-value {
    color: #666;
  }

  .btn-remove {
    width: 30px;
    height: 30px;
    background: #dc3545;
    color: white;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    font-size: 1.5rem;
    line-height: 1;
    transition: background 0.2s;
  }

  .btn-remove:hover {
    background: #c82333;
  }

  .empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: #666;
    background: #f8f9fa;
    border-radius: 4px;
  }
</style>
