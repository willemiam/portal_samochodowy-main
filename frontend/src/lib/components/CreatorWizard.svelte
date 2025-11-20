<script lang="ts">
  import { wizardStore } from '../stores/wizardStore';
  import { createPlatform } from '../api/platform';
  import StepBasicInfo from './StepBasicInfo.svelte';
  import StepFeatures from './StepFeatures.svelte';
  import StepDomainDetails from './StepDomainDetails.svelte';
  import StepAdvanced from './StepAdvanced.svelte';
  import StepSummary from './StepSummary.svelte';

  let state = $state($wizardStore);

  $effect(() => {
    state = $wizardStore;
  });

  const steps = [
    { title: 'Basic Info', component: StepBasicInfo },
    { title: 'Features', component: StepFeatures },
    { title: 'Domain Details', component: StepDomainDetails },
    { title: 'Advanced', component: StepAdvanced },
    { title: 'Summary', component: StepSummary },
  ];

  function canProceed(): boolean {
    const config = state.platformConfig;
    
    switch (state.currentStep) {
      case 0: // Basic Info
        return !!(config.name && config.domain);
      case 1: // Features
        return true;
      case 2: // Domain Details
        return !!(config.domainDetails.itemName && config.domainDetails.itemNamePlural);
      case 3: // Advanced
        return true;
      case 4: // Summary
        return true;
      default:
        return false;
    }
  }

  function handleNext() {
    if (canProceed() && state.currentStep < steps.length - 1) {
      wizardStore.nextStep();
    }
  }

  function handlePrev() {
    wizardStore.prevStep();
  }

  async function handleSave() {
    wizardStore.setSaving(true);
    wizardStore.setError(null);

    try {
      const response = await createPlatform(state.platformConfig);
      wizardStore.setPlatformId(response.id);
      alert(`Platform created successfully! ID: ${response.id}`);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save platform';
      wizardStore.setError(errorMessage);
      alert(`Error: ${errorMessage}`);
    } finally {
      wizardStore.setSaving(false);
    }
  }

  function handleReset() {
    if (confirm('Are you sure you want to reset the wizard? All progress will be lost.')) {
      wizardStore.reset();
    }
  }
</script>

<div class="wizard-container">
  <div class="wizard-header">
    <h1>Platform Creator Wizard</h1>
    <p>Create your custom platform in a few simple steps</p>
  </div>

  <div class="wizard-progress">
    {#each steps as step, index}
      <div 
        class="progress-step"
        class:active={index === state.currentStep}
        class:completed={index < state.currentStep}
      >
        <div class="step-number">{index + 1}</div>
        <div class="step-title">{step.title}</div>
      </div>
      {#if index < steps.length - 1}
        <div class="progress-line" class:completed={index < state.currentStep}></div>
      {/if}
    {/each}
  </div>

  <div class="wizard-content">
    {#if state.error}
      <div class="error-banner">
        <strong>Error:</strong> {state.error}
        <button onclick={() => wizardStore.setError(null)}>×</button>
      </div>
    {/if}

    {#if state.platformId}
      <div class="success-banner">
        <strong>Success!</strong> Platform created with ID: {state.platformId}
      </div>
    {/if}

    <svelte:component this={steps[state.currentStep].component} />
  </div>

  <div class="wizard-footer">
    <div class="footer-left">
      <button 
        type="button"
        onclick={handleReset}
        class="btn btn-secondary"
      >
        Reset
      </button>
    </div>

    <div class="footer-right">
      {#if state.currentStep > 0}
        <button 
          type="button"
          onclick={handlePrev}
          class="btn btn-secondary"
        >
          Previous
        </button>
      {/if}

      {#if state.currentStep < steps.length - 1}
        <button 
          type="button"
          onclick={handleNext}
          disabled={!canProceed()}
          class="btn btn-primary"
        >
          Next
        </button>
      {:else}
        <button 
          type="button"
          onclick={handleSave}
          disabled={state.isSaving || !canProceed()}
          class="btn btn-primary"
        >
          {state.isSaving ? 'Saving...' : state.platformId ? 'Update' : 'Save Platform'}
        </button>
      {/if}
    </div>
  </div>
</div>

<style>
  .wizard-container {
    max-width: 1000px;
    margin: 2rem auto;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    overflow: hidden;
  }

  .wizard-header {
    background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
    color: white;
    padding: 2rem;
    text-align: center;
  }

  .wizard-header h1 {
    margin: 0 0 0.5rem 0;
    font-size: 2rem;
  }

  .wizard-header p {
    margin: 0;
    opacity: 0.9;
  }

  .wizard-progress {
    display: flex;
    align-items: center;
    padding: 2rem;
    background-color: #f9f9f9;
    overflow-x: auto;
  }

  .progress-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    min-width: 80px;
  }

  .step-number {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: #e0e0e0;
    color: #666;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    transition: all 0.3s;
  }

  .progress-step.active .step-number {
    background-color: #4CAF50;
    color: white;
    transform: scale(1.1);
  }

  .progress-step.completed .step-number {
    background-color: #2e7d32;
    color: white;
  }

  .step-title {
    font-size: 0.875rem;
    color: #666;
    text-align: center;
  }

  .progress-step.active .step-title {
    color: #4CAF50;
    font-weight: 600;
  }

  .progress-line {
    flex: 1;
    height: 2px;
    background-color: #e0e0e0;
    margin: 0 0.5rem;
    min-width: 20px;
    transition: background-color 0.3s;
  }

  .progress-line.completed {
    background-color: #4CAF50;
  }

  .wizard-content {
    min-height: 400px;
    padding: 1rem;
  }

  .error-banner,
  .success-banner {
    margin: 1rem 2rem;
    padding: 1rem;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .error-banner {
    background-color: #ffebee;
    border-left: 4px solid #f44336;
    color: #c62828;
  }

  .success-banner {
    background-color: #e8f5e9;
    border-left: 4px solid #4CAF50;
    color: #2e7d32;
  }

  .error-banner button {
    background: none;
    border: none;
    color: #c62828;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .wizard-footer {
    display: flex;
    justify-content: space-between;
    padding: 2rem;
    background-color: #f9f9f9;
    border-top: 1px solid #e0e0e0;
  }

  .footer-left,
  .footer-right {
    display: flex;
    gap: 1rem;
  }

  .btn {
    padding: 0.75rem 2rem;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-primary {
    background-color: #4CAF50;
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    background-color: #45a049;
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }

  .btn-secondary {
    background-color: #e0e0e0;
    color: #333;
  }

  .btn-secondary:hover {
    background-color: #d5d5d5;
  }
</style>
