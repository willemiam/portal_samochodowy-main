<script lang="ts">
  import { wizardStore } from '../stores/wizardStore';
  
  let domain = '';
  let itemFields: string = '';
  let customSettings: string = '';
  
  // Load current values
  wizardStore.subscribe(config => {
    domain = config.domain;
    itemFields = JSON.stringify(config.domainDetails.itemFields || [], null, 2);
    customSettings = JSON.stringify(config.domainDetails.customSettings || {}, null, 2);
  });
  
  function updateStore() {
    let parsedFields = [];
    let parsedSettings = {};
    
    try {
      parsedFields = JSON.parse(itemFields || '[]');
    } catch (e) {
      console.warn('Invalid JSON for item fields');
    }
    
    try {
      parsedSettings = JSON.parse(customSettings || '{}');
    } catch (e) {
      console.warn('Invalid JSON for custom settings');
    }
    
    wizardStore.update(config => ({
      ...config,
      domainDetails: {
        itemFields: parsedFields,
        customSettings: parsedSettings
      }
    }));
  }
</script>

<div class="step-container">
  <h2>Domain Details</h2>
  <p>Configure domain-specific settings for "{domain || 'your domain'}"</p>
  
  <div class="info-box">
    <strong>Note:</strong> This is a placeholder step. In future versions, this will be 
    dynamically generated based on your selected domain.
  </div>
  
  <div class="form-group">
    <label for="itemFields">Item Fields (JSON)</label>
    <textarea 
      id="itemFields"
      bind:value={itemFields}
      on:blur={updateStore}
      placeholder='["field1", "field2", "field3"]'
      rows="6"
    ></textarea>
    <small>Define the fields for items in your domain (JSON array format)</small>
  </div>
  
  <div class="form-group">
    <label for="customSettings">Custom Settings (JSON)</label>
    <textarea 
      id="customSettings"
      bind:value={customSettings}
      on:blur={updateStore}
      placeholder='&#123;"setting1": "value1", "setting2": "value2"&#125;'
      rows="6"
    ></textarea>
    <small>Add any custom domain-specific settings (JSON object format)</small>
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
    background-color: #e3f2fd;
    border-left: 4px solid #2196F3;
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
  
  textarea {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    font-family: 'Courier New', monospace;
    resize: vertical;
  }
  
  textarea:focus {
    outline: none;
    border-color: #4CAF50;
  }
  
  small {
    display: block;
    margin-top: 5px;
    color: #999;
    font-size: 12px;
  }
</style>
