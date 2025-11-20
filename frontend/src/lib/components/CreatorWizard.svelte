<script lang="ts">
  import StepBasicInfo from './StepBasicInfo.svelte';
  import StepFeatures from './StepFeatures.svelte';
  import StepDomainDetails from './StepDomainDetails.svelte';
  import StepAdvanced from './StepAdvanced.svelte';
  import StepSummary from './StepSummary.svelte';
  import { wizardStore } from '../stores/wizardStore';
  
  let currentStep = 0;
  let config: any = {};
  
  const steps = [
    { title: 'Basic Info', component: StepBasicInfo },
    { title: 'Features', component: StepFeatures },
    { title: 'Domain Details', component: StepDomainDetails },
    { title: 'Advanced', component: StepAdvanced },
    { title: 'Summary', component: StepSummary }
  ];
  
  wizardStore.subscribe(c => {
    config = c;
  });
  
  function nextStep() {
    if (currentStep < steps.length - 1) {
      currentStep++;
    }
  }
  
  function prevStep() {
    if (currentStep > 0) {
      currentStep--;
    }
  }
  
  function goToStep(index: number) {
    currentStep = index;
  }
  
  function canProceed(): boolean {
    if (currentStep === 0) {
      return !!(config.name && config.description && config.domain);
    }
    return true;
  }
</script>

<div class="wizard-container">
  <div class="wizard-header">
    <h1>Platform Creator Wizard</h1>
    <p>Create and configure your custom platform</p>
  </div>
  
  <div class="step-indicator">
    {#each steps as step, index}
      <div 
        class="step-item" 
        class:active={index === currentStep}
        class:completed={index < currentStep}
        on:click={() => goToStep(index)}
        role="button"
        tabindex="0"
      >
        <div class="step-number">{index + 1}</div>
        <div class="step-title">{step.title}</div>
      </div>
    {/each}
  </div>
  
  <div class="step-content">
    <svelte:component this={steps[currentStep].component} />
  </div>
  
  <div class="wizard-navigation">
    <button 
      class="btn btn-secondary" 
      on:click={prevStep}
      disabled={currentStep === 0}
    >
      Previous
    </button>
    
    {#if currentStep < steps.length - 1}
      <button 
        class="btn btn-primary" 
        on:click={nextStep}
        disabled={!canProceed()}
      >
        Next
      </button>
    {/if}
  </div>
</div>

<style>
  .wizard-container {
    max-width: 1000px;
    margin: 40px auto;
    padding: 20px;
  }
  
  .wizard-header {
    text-align: center;
    margin-bottom: 40px;
  }
  
  .wizard-header h1 {
    margin-bottom: 10px;
    color: #333;
  }
  
  .wizard-header p {
    color: #666;
  }
  
  .step-indicator {
    display: flex;
    justify-content: space-between;
    margin-bottom: 40px;
    padding: 0 20px;
  }
  
  .step-item {
    flex: 1;
    text-align: center;
    cursor: pointer;
    position: relative;
    padding: 10px 5px;
  }
  
  .step-item:not(:last-child)::after {
    content: '';
    position: absolute;
    top: 25px;
    right: -50%;
    width: 100%;
    height: 2px;
    background-color: #ddd;
    z-index: -1;
  }
  
  .step-item.completed:not(:last-child)::after {
    background-color: #4CAF50;
  }
  
  .step-number {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: #ddd;
    color: #666;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 8px;
    font-weight: bold;
    transition: all 0.3s;
  }
  
  .step-item.active .step-number {
    background-color: #4CAF50;
    color: white;
    transform: scale(1.1);
  }
  
  .step-item.completed .step-number {
    background-color: #4CAF50;
    color: white;
  }
  
  .step-title {
    font-size: 14px;
    color: #666;
  }
  
  .step-item.active .step-title {
    color: #4CAF50;
    font-weight: 500;
  }
  
  .step-content {
    min-height: 400px;
    margin-bottom: 40px;
  }
  
  .wizard-navigation {
    display: flex;
    justify-content: space-between;
    padding: 20px;
    border-top: 1px solid #eee;
  }
  
  .btn {
    padding: 12px 30px;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.2s;
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
  }
  
  .btn-secondary {
    background-color: #757575;
    color: white;
  }
  
  .btn-secondary:hover:not(:disabled) {
    background-color: #616161;
  }
</style>
