<script>
  import { onMount } from "svelte";
  import { navigate } from "svelte-routing";
  import { isLoading, error, selectedExperiment } from "../stores/store";
  import {
    createExperiment,
    getAvailableModels,
    runExperiment,
  } from "../lib/experimentsApi";

  let availableModels = [];
  let experimentName = "";
  let experimentDescription = "";
  let selectedModels = [];
  let temperature = 0.3;
  let maxTokens = 256;
  let gapNotation = "auto";
  let testItems = [];
  let testItemText = "";
  let showResults = false;
  let results = null;

  onMount(async () => {
    try {
      isLoading.set(true);
      const models = await getAvailableModels();
      availableModels = models.map((m) => m.name);
    } catch (err) {
      error.set(err.message);
    } finally {
      isLoading.set(false);
    }
  });

  function toggleModel(modelName) {
    if (selectedModels.includes(modelName)) {
      selectedModels = selectedModels.filter((m) => m !== modelName);
    } else {
      selectedModels = [...selectedModels, modelName];
    }
  }

  function addTestItem() {
    if (testItemText.trim()) {
      testItems = [
        ...testItems,
        {
          id: `item-${Date.now()}`,
          text_with_gaps: testItemText.trim(),
        },
      ];
      testItemText = "";
    }
  }

  function removeTestItem(id) {
    testItems = testItems.filter((item) => item.id !== id);
  }

  async function handleCreateExperiment() {
    if (
      !experimentName.trim() ||
      selectedModels.length === 0 ||
      testItems.length === 0
    ) {
      error.set(
        "Please fill in experiment name, select models, and add test items"
      );
      return;
    }

    try {
      isLoading.set(true);
      error.set(null);

      // Create experiment
      const experiment = {
        name: experimentName,
        description: experimentDescription,
        models: selectedModels,
        parameters: {
          temperature,
          max_tokens: maxTokens,
          gap_notation: gapNotation,
        },
      };

      const createdExp = await createExperiment(experiment);
      selectedExperiment.set(createdExp);

      // Run experiment
      const runResults = await runExperiment(createdExp.id, testItems);
      results = runResults;
      showResults = true;
    } catch (err) {
      error.set(err.message);
    } finally {
      isLoading.set(false);
    }
  }
</script>

<div class="experiments-page">
  <div class="container">
    <h1>Create A/B Testing Experiment</h1>

    {#if showResults}
      <div class="results-view">
        <div class="results-header">
          <h2>Experiment Results</h2>
          <button
            class="btn btn-outline"
            on:click={() => (showResults = false)}
          >
            Back to Setup
          </button>
        </div>

        <div class="results-container">
          <div class="results-summary">
            <p>
              <strong>Experiment:</strong>
              {experimentName}
            </p>
            <p>
              <strong>Models:</strong>
              {selectedModels.join(", ")}
            </p>
            <p>
              <strong>Test Items:</strong>
              {testItems.length}
            </p>
          </div>

          <!-- Results Table -->
          <div class="results-table-wrapper">
            <table class="results-table">
              <thead>
                <tr>
                  <th>Item</th>
                  <th>Model</th>
                  <th>Original Text</th>
                  <th>Filled Text</th>
                  <th>Score</th>
                  <th>Time (s)</th>
                </tr>
              </thead>
              <tbody>
                {#if results && results.results}
                  {#each results.results as run}
                    <tr>
                      <td>{run.item_id}</td>
                      <td>{run.model_name}</td>
                      <td class="text-cell">{run.original_text}</td>
                      <td class="text-cell filled">{run.filled_text}</td>
                      <td>
                        {run.overall_score ? run.overall_score.toFixed(2) : "N/A"}
                      </td>
                      <td>
                        {run.generation_time ? run.generation_time.toFixed(2) : "N/A"}
                      </td>
                    </tr>
                  {/each}
                {/if}
              </tbody>
            </table>
          </div>

          <!-- Comparison View -->
          <div class="comparison-section">
            <h3>Model Comparison</h3>
            <div class="comparison-grid">
              {#each selectedModels as model}
                <div class="model-card">
                  <h4>{model}</h4>
                  {#if results && results.results}
                    {@const modelResults = results.results.filter(
                      (r) => r.model_name === model
                    )}
                    <p>
                      <strong>Avg Score:</strong>
                      {(
                        modelResults.reduce((sum, r) => sum + (r.overall_score || 0), 0) /
                        modelResults.length
                      ).toFixed(2)}
                    </p>
                    <p>
                      <strong>Avg Time:</strong>
                      {(
                        modelResults.reduce((sum, r) => sum + (r.generation_time || 0), 0) /
                        modelResults.length
                      ).toFixed(2)}s
                    </p>
                  {/if}
                </div>
              {/each}
            </div>
          </div>
        </div>
      </div>
    {:else}
      <form on:submit|preventDefault={handleCreateExperiment} class="experiment-form">
        <!-- Experiment Info -->
        <div class="form-section">
          <h2>Experiment Information</h2>
          <div class="form-group">
            <label for="name">Experiment Name *</label>
            <input
              id="name"
              type="text"
              bind:value={experimentName}
              placeholder="e.g., Bielik vs Llama Comparison"
              required
            />
          </div>

          <div class="form-group">
            <label for="description">Description</label>
            <textarea
              id="description"
              bind:value={experimentDescription}
              placeholder="Optional: describe the purpose of this experiment"
              rows="3"
            />
          </div>
        </div>

        <!-- Model Selection -->
        <div class="form-section">
          <h2>Select Models *</h2>
          <div class="models-list">
            {#each availableModels as model}
              <label class="model-checkbox">
                <input
                  type="checkbox"
                  checked={selectedModels.includes(model)}
                  on:change={() => toggleModel(model)}
                />
                <span>{model}</span>
              </label>
            {/each}
          </div>
          {#if selectedModels.length === 0}
            <p class="validation-error">Select at least one model</p>
          {/if}
        </div>

        <!-- Parameters -->
        <div class="form-section">
          <h2>Generation Parameters</h2>
          <div class="form-group">
            <label for="temperature">
              Temperature: <span class="value">{temperature}</span>
            </label>
            <input
              id="temperature"
              type="range"
              min="0"
              max="1"
              step="0.1"
              bind:value={temperature}
            />
            <small>Lower values = more deterministic, higher = more creative</small>
          </div>

          <div class="form-group">
            <label for="maxTokens">Max Tokens</label>
            <input
              id="maxTokens"
              type="number"
              bind:value={maxTokens}
              min="50"
              max="512"
            />
          </div>

          <div class="form-group">
            <label for="gapNotation">Gap Notation</label>
            <select id="gapNotation" bind:value={gapNotation}>
              <option value="auto">Auto Detect</option>
              <option value="[GAP:n]">[GAP:n]</option>
              <option value="___">Underscores (___)</option>
            </select>
          </div>
        </div>

        <!-- Test Items -->
        <div class="form-section">
          <h2>Test Items *</h2>
          <div class="test-item-input">
            <textarea
              bind:value={testItemText}
              placeholder='Enter text with gaps, e.g., "Sprzedam [GAP:1] BMW w [GAP:2] stanie technicznym"'
              rows="3"
            />
            <button
              type="button"
              class="btn btn-outline"
              on:click={addTestItem}
              disabled={!testItemText.trim()}
            >
              Add Item
            </button>
          </div>

          {#if testItems.length === 0}
            <p class="validation-error">Add at least one test item</p>
          {:else}
            <div class="test-items-list">
              <h3>Test Items ({testItems.length})</h3>
              {#each testItems as item (item.id)}
                <div class="test-item">
                  <p>{item.text_with_gaps}</p>
                  <button
                    type="button"
                    class="btn-remove"
                    on:click={() => removeTestItem(item.id)}
                  >
                    Remove
                  </button>
                </div>
              {/each}
            </div>
          {/if}
        </div>

        {#if $error}
          <div class="error-message">{$error}</div>
        {/if}

        <!-- Submit -->
        <div class="form-actions">
          <button
            type="submit"
            class="btn btn-primary"
            disabled={$isLoading}
          >
            {$isLoading ? "Running Experiment..." : "Run Experiment"}
          </button>
        </div>
      </form>
    {/if}
  </div>
</div>

<style>
  .experiments-page {
    min-height: 100vh;
    background-color: var(--light-gray);
    padding: 2rem 0;
  }

  .container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 0 1rem;
  }

  h1 {
    font-size: 2rem;
    margin-bottom: 2rem;
    color: var(--primary-color);
  }

  .experiment-form {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .form-section {
    margin-bottom: 2.5rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid var(--light-gray);
  }

  .form-section:last-of-type {
    border-bottom: none;
  }

  .form-section h2 {
    font-size: 1.3rem;
    margin-bottom: 1rem;
    color: var(--primary-color);
  }

  .form-group {
    margin-bottom: 1.5rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: var(--dark-gray);
  }

  .form-group .value {
    font-weight: bold;
    color: var(--accent-color);
  }

  .form-group input[type="text"],
  .form-group input[type="number"],
  .form-group textarea,
  .form-group select {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid var(--mid-gray);
    border-radius: 4px;
    font-size: 1rem;
    font-family: inherit;
  }

  .form-group input[type="range"] {
    width: 100%;
    height: 6px;
    cursor: pointer;
  }

  .form-group small {
    display: block;
    margin-top: 0.25rem;
    color: #666;
    font-size: 0.85rem;
  }

  .models-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem;
  }

  .model-checkbox {
    display: flex;
    align-items: center;
    cursor: pointer;
    padding: 0.75rem;
    border: 1px solid var(--mid-gray);
    border-radius: 4px;
    transition: all 0.2s ease;
  }

  .model-checkbox input {
    margin-right: 0.5rem;
  }

  .model-checkbox:hover {
    background-color: var(--light-gray);
  }

  .test-item-input {
    display: flex;
    gap: 1rem;
    align-items: flex-start;
    margin-bottom: 1rem;
  }

  .test-item-input textarea {
    flex: 1;
  }

  .test-item-input button {
    align-self: flex-end;
    min-height: 44px;
  }

  .test-items-list {
    margin-top: 1.5rem;
  }

  .test-items-list h3 {
    font-size: 1rem;
    margin-bottom: 1rem;
    color: var(--dark-gray);
  }

  .test-item {
    background: var(--light-gray);
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .test-item p {
    flex: 1;
    margin: 0;
    font-size: 0.9rem;
  }

  .btn-remove {
    background: var(--danger);
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    margin-left: 1rem;
    font-size: 0.85rem;
  }

  .btn-remove:hover {
    background: #c82828;
  }

  .validation-error {
    color: var(--danger);
    font-size: 0.9rem;
    margin-top: 0.5rem;
  }

  .error-message {
    background-color: #ffe6e6;
    color: var(--danger);
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1rem;
  }

  .form-actions {
    margin-top: 2rem;
    display: flex;
    gap: 1rem;
  }

  .form-actions button {
    min-height: 44px;
  }

  /* Results View */
  .results-view {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }

  .results-header h2 {
    margin: 0;
  }

  .results-summary {
    background: var(--light-gray);
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 2rem;
  }

  .results-summary p {
    margin: 0.5rem 0;
  }

  .results-table-wrapper {
    overflow-x: auto;
    margin-bottom: 2rem;
  }

  .results-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
  }

  .results-table th {
    background: var(--primary-color);
    color: white;
    padding: 0.75rem;
    text-align: left;
    font-weight: 600;
  }

  .results-table td {
    padding: 0.75rem;
    border-bottom: 1px solid var(--light-gray);
  }

  .results-table tbody tr:hover {
    background: var(--light-gray);
  }

  .text-cell {
    max-width: 200px;
    word-break: break-word;
  }

  .text-cell.filled {
    background: #e6f7e6;
  }

  .comparison-section {
    margin-top: 2rem;
  }

  .comparison-section h3 {
    margin-bottom: 1rem;
  }

  .comparison-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }

  .model-card {
    background: var(--light-gray);
    padding: 1rem;
    border-radius: 4px;
    border-left: 4px solid var(--accent-color);
  }

  .model-card h4 {
    margin-top: 0;
  }

  .model-card p {
    margin: 0.5rem 0;
  }

  @media (max-width: 768px) {
    .test-item-input {
      flex-direction: column;
    }

    .test-item {
      flex-direction: column;
      align-items: flex-start;
    }

    .btn-remove {
      margin-left: 0;
      margin-top: 0.5rem;
    }

    .results-table {
      font-size: 0.8rem;
    }

    .results-table th,
    .results-table td {
      padding: 0.5rem;
    }
  }
</style>
