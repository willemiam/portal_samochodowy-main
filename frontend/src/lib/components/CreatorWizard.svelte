<script lang="ts">
  import { wizardStore } from '../stores/wizardStore';
  import StepBasicInfo from './StepBasicInfo.svelte';
  import StepFeatures from './StepFeatures.svelte';
  import StepDomainDetails from './StepDomainDetails.svelte';
  import StepAdvanced from './StepAdvanced.svelte';
  import StepSummary from './StepSummary.svelte';

  const steps = [
    { title: 'Basic Info', component: StepBasicInfo },
    { title: 'Features', component: StepFeatures },
    { title: 'Domain Details', component: StepDomainDetails },
    { title: 'Advanced', component: StepAdvanced },
    { title: 'Summary', component: StepSummary }
  ];

  let currentStepValue = 0;
  
  wizardStore.subscribe(state => {
    currentStepValue = state.currentStep;
  });

  function handlePrevious() {
    wizardStore.prevStep();
  }

  function handleNext() {
    wizardStore.nextStep();
  }
</script>

<div class="wizard-container">
  <h1>Platform Creator Wizard</h1>
  
  <!-- Step Progress Indicator -->
  <div class="progress-bar">
    {#each steps as step, index}
      <div class="progress-step" class:active={index === currentStepValue} class:completed={index < currentStepValue}>
        <div class="step-number">{index + 1}</div>
        <div class="step-title">{step.title}</div>
      </div>
    {/each}
  </div>

  <!-- Step Content -->
  <div class="step-content">
    {#if currentStepValue === 0}
      <StepBasicInfo />
    {:else if currentStepValue === 1}
      <StepFeatures />
    {:else if currentStepValue === 2}
      <StepDomainDetails />
    {:else if currentStepValue === 3}
      <StepAdvanced />
    {:else if currentStepValue === 4}
      <StepSummary />
    {/if}
  </div>

  <!-- Navigation Buttons -->
  <div class="navigation-buttons">
    {#if currentStepValue > 0}
      <button class="btn btn-secondary" on:click={handlePrevious}>
        Previous
      </button>
    {/if}
    
    {#if currentStepValue < steps.length - 1}
      <button class="btn btn-primary" on:click={handleNext}>
        Next
      </button>
    {/if}
  </div>
</div>

<style>
  .wizard-container {
    max-width: 800px;
    margin: 2rem auto;
    padding: 2rem;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  h1 {
    text-align: center;
    color: #333;
    margin-bottom: 2rem;
  }

  .progress-bar {
    display: flex;
    justify-content: space-between;
    margin-bottom: 3rem;
    position: relative;
  }

  .progress-bar::before {
    content: '';
    position: absolute;
    top: 20px;
    left: 10%;
    right: 10%;
    height: 2px;
    background: #e0e0e0;
    z-index: 0;
  }

  .progress-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
    z-index: 1;
    flex: 1;
  }

  .step-number {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #e0e0e0;
    color: #666;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    margin-bottom: 0.5rem;
  }

  .progress-step.active .step-number {
    background: #007bff;
    color: white;
  }

  .progress-step.completed .step-number {
    background: #28a745;
    color: white;
  }

  .step-title {
    font-size: 0.85rem;
    color: #666;
    text-align: center;
  }

  .progress-step.active .step-title {
    color: #007bff;
    font-weight: 600;
  }

  .step-content {
    min-height: 300px;
    padding: 2rem 0;
  }

  .navigation-buttons {
    display: flex;
    justify-content: space-between;
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid #e0e0e0;
  }

  .btn {
    padding: 0.75rem 2rem;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-primary {
    background: #007bff;
    color: white;
  }

  .btn-primary:hover {
    background: #0056b3;
  }

  .btn-secondary {
    background: #6c757d;
    color: white;
  }

  .btn-secondary:hover {
    background: #545b62;
  }
</style>
