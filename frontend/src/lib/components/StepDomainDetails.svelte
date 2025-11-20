<script lang="ts">
  import { wizardStore } from '../stores/wizardStore';

  let targetAudience = '';
  let primaryGoals: string[] = [];
  
  const availableGoals = [
    'Increase user engagement',
    'Improve conversion rates',
    'Enhance user experience',
    'Streamline operations',
    'Generate insights',
    'Build community',
    'Scale infrastructure',
    'Reduce costs'
  ];

  wizardStore.subscribe(state => {
    targetAudience = state.platformData.targetAudience;
    primaryGoals = state.platformData.primaryGoals || [];
  });

  function handleAudienceUpdate() {
    wizardStore.updatePlatformData({ targetAudience });
  }

  function toggleGoal(goal: string) {
    if (primaryGoals.includes(goal)) {
      primaryGoals = primaryGoals.filter(g => g !== goal);
    } else {
      primaryGoals = [...primaryGoals, goal];
    }
    wizardStore.updatePlatformData({ primaryGoals });
  }

  function isGoalSelected(goal: string): boolean {
    return primaryGoals.includes(goal);
  }
</script>

<div class="step-container">
  <h2>Domain Details</h2>
  <p class="step-description">Define your target audience and primary goals</p>

  <div class="form-group">
    <label for="targetAudience">Target Audience *</label>
    <textarea
      id="targetAudience"
      bind:value={targetAudience}
      on:blur={handleAudienceUpdate}
      placeholder="Describe your target users (e.g., car buyers, dealers, enthusiasts)..."
      rows="3"
      required
    ></textarea>
  </div>

  <div class="form-group">
    <label>Primary Goals</label>
    <div class="goals-grid">
      {#each availableGoals as goal}
        <div
          class="goal-item"
          class:selected={isGoalSelected(goal)}
          on:click={() => toggleGoal(goal)}
          on:keypress={(e) => e.key === 'Enter' && toggleGoal(goal)}
          role="button"
          tabindex="0"
        >
          <input
            type="checkbox"
            checked={isGoalSelected(goal)}
            on:click|stopPropagation
            on:change={() => toggleGoal(goal)}
          />
          <span>{goal}</span>
        </div>
      {/each}
    </div>
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
    margin-bottom: 2rem;
  }

  label {
    display: block;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: #333;
  }

  textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    font-family: inherit;
    resize: vertical;
  }

  textarea:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
  }

  .goals-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 0.75rem;
  }

  .goal-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
    background: white;
  }

  .goal-item:hover {
    border-color: #007bff;
    background: #f8f9fa;
  }

  .goal-item.selected {
    border-color: #007bff;
    background: #e7f3ff;
  }

  .goal-item input[type="checkbox"] {
    cursor: pointer;
  }

  .goal-item span {
    flex: 1;
    color: #333;
  }
</style>
