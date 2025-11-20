<script lang="ts">
  import { wizardStore } from '../stores/wizardStore';
  
  let theme = 'light';
  let language = 'en';
  let otherSettings: string = '';
  
  // Load current values
  wizardStore.subscribe(config => {
    theme = config.advanced.theme || 'light';
    language = config.advanced.language || 'en';
    const { theme: _, language: __, ...rest } = config.advanced;
    otherSettings = JSON.stringify(rest, null, 2);
  });
  
  function updateStore() {
    let parsedOther = {};
    
    try {
      parsedOther = JSON.parse(otherSettings || '{}');
    } catch (e) {
      console.warn('Invalid JSON for other settings');
    }
    
    wizardStore.update(config => ({
      ...config,
      advanced: {
        theme,
        language,
        ...parsedOther
      }
    }));
  }
</script>

<div class="step-container">
  <h2>Advanced Settings</h2>
  <p>Configure advanced options for your platform</p>
  
  <div class="info-box">
    <strong>Optional:</strong> These settings can be customized later if needed.
  </div>
  
  <div class="form-group">
    <label for="theme">Theme</label>
    <select id="theme" bind:value={theme} on:change={updateStore}>
      <option value="light">Light</option>
      <option value="dark">Dark</option>
      <option value="auto">Auto</option>
    </select>
  </div>
  
  <div class="form-group">
    <label for="language">Default Language</label>
    <select id="language" bind:value={language} on:change={updateStore}>
      <option value="en">English</option>
      <option value="pl">Polish</option>
      <option value="de">German</option>
      <option value="fr">French</option>
    </select>
  </div>
  
  <div class="form-group">
    <label for="otherSettings">Other Settings (JSON)</label>
    <textarea 
      id="otherSettings"
      bind:value={otherSettings}
      on:blur={updateStore}
      placeholder='&#123;"customSetting": "value"&#125;'
      rows="6"
    ></textarea>
    <small>Add any additional configuration as JSON</small>
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
    margin-bottom: 20px;
  }
  
  .info-box {
    background-color: #fff3e0;
    border-left: 4px solid #ff9800;
    padding: 15px;
    margin-bottom: 30px;
    border-radius: 4px;
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
  
  select, textarea {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
  }
  
  select:focus, textarea:focus {
    outline: none;
    border-color: #4CAF50;
  }
  
  textarea {
    font-family: 'Courier New', monospace;
    resize: vertical;
  }
  
  small {
    display: block;
    margin-top: 5px;
    color: #999;
    font-size: 12px;
  }
</style>
