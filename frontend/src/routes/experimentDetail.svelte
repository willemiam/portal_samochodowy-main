<script>
  import { onMount } from "svelte";
  import { navigate } from "svelte-routing";
  import { isLoading, error } from "../stores/store";
  import {
    getExperimentResults,
    exportResults,
    deleteExperiment,
  } from "../lib/experimentsApi";

  export let params;

  let experimentId = params.id;
  let experimentData = null;
  let results = null;

  onMount(async () => {
    try {
      isLoading.set(true);
      const data = await getExperimentResults(experimentId);
      results = data;
    } catch (err) {
      error.set(err.message);
    } finally {
      isLoading.set(false);
    }
  });

  async function handleExport() {
    try {
      await exportResults(experimentId);
    } catch (err) {
      error.set(err.message);
    }
  }

  async function handleDelete() {
    if (confirm("Are you sure you want to delete this experiment?")) {
      try {
        await deleteExperiment(experimentId);
        navigate("/");
      } catch (err) {
        error.set(err.message);
      }
    }
  }

  function calculateAverages(results) {
    const groupedByModel = {};

    results.forEach((run) => {
      if (!groupedByModel[run.model_name]) {
        groupedByModel[run.model_name] = {
          scores: [],
          times: [],
          count: 0,
        };
      }
      groupedByModel[run.model_name].scores.push(run.overall_score || 0);
      groupedByModel[run.model_name].times.push(run.generation_time || 0);
      groupedByModel[run.model_name].count++;
    });

    return Object.entries(groupedByModel).map(([model, data]) => ({
      model,
      avgScore: (data.scores.reduce((a, b) => a + b, 0) / data.count).toFixed(2),
      avgTime: (data.times.reduce((a, b) => a + b, 0) / data.count).toFixed(2),
      count: data.count,
    }));
  }
</script>

<div class="detail-page">
  <div class="container">
    <div class="detail-header">
      <h1>Experiment Results</h1>
      <div class="header-actions">
        <button class="btn btn-primary" on:click={handleExport}>
          Export CSV
        </button>
        <button class="btn btn-outline" on:click={() => navigate("/")}>
          Back
        </button>
      </div>
    </div>

    {#if $isLoading}
      <div class="loading">Loading experiment results...</div>
    {:else if $error}
      <div class="error-message">{$error}</div>
    {:else if results && results.results}
      <div class="detail-content">
        <!-- Summary -->
        <div class="summary-section">
          <div class="summary-card">
            <h3>Experiment</h3>
            <p>{results.experiment_name}</p>
          </div>
          <div class="summary-card">
            <h3>Models Compared</h3>
            <p>{results.models_compared.join(", ")}</p>
          </div>
          <div class="summary-card">
            <h3>Test Items</h3>
            <p>{results.total_items}</p>
          </div>
        </div>

        <!-- Model Comparison -->
        <div class="comparison-section">
          <h2>Model Performance Summary</h2>
          <div class="comparison-grid">
            {#each calculateAverages(results.results) as modelStats}
              <div class="stat-card">
                <h4>{modelStats.model}</h4>
                <div class="stat">
                  <span class="label">Avg Score:</span>
                  <span class="value">{modelStats.avgScore}</span>
                </div>
                <div class="stat">
                  <span class="label">Avg Time:</span>
                  <span class="value">{modelStats.avgTime}s</span>
                </div>
                <div class="stat">
                  <span class="label">Items:</span>
                  <span class="value">{modelStats.count}</span>
                </div>
              </div>
            {/each}
          </div>
        </div>

        <!-- Detailed Results Table -->
        <div class="results-section">
          <h2>Detailed Results</h2>
          <div class="table-wrapper">
            <table class="results-table">
              <thead>
                <tr>
                  <th>Item ID</th>
                  <th>Model</th>
                  <th>Original Text</th>
                  <th>Filled Text</th>
                  <th>Semantic Score</th>
                  <th>Domain Score</th>
                  <th>Grammar Score</th>
                  <th>Overall Score</th>
                  <th>Time (s)</th>
                </tr>
              </thead>
              <tbody>
                {#each results.results as run}
                  <tr>
                    <td>{run.item_id}</td>
                    <td><strong>{run.model_name}</strong></td>
                    <td class="text-cell">{run.original_text}</td>
                    <td class="text-cell filled">{run.filled_text}</td>
                    <td>
                      {run.semantic_score ? run.semantic_score.toFixed(2) : "N/A"}
                    </td>
                    <td>
                      {run.domain_score ? run.domain_score.toFixed(2) : "N/A"}
                    </td>
                    <td>
                      {run.grammar_score ? run.grammar_score.toFixed(2) : "N/A"}
                    </td>
                    <td class="overall">
                      {run.overall_score ? run.overall_score.toFixed(2) : "N/A"}
                    </td>
                    <td>
                      {run.generation_time ? run.generation_time.toFixed(2) : "N/A"}
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>

        <!-- Gap Analysis -->
        <div class="gaps-section">
          <h2>Gap Fill Analysis (Sample)</h2>
          {#if results.results.length > 0}
            {@const firstResult = results.results[0]}
            <div class="gap-analysis">
              <p><strong>Item:</strong> {firstResult.original_text}</p>
              {#if firstResult.gaps && firstResult.gaps.length > 0}
                <div class="gaps-list">
                  {#each firstResult.gaps as gap}
                    <div class="gap-item">
                      <span class="gap-index">[{gap.index}]</span>
                      <span class="gap-choice">→ {gap.choice}</span>
                      {#if gap.alternatives && gap.alternatives.length > 0}
                        <span class="gap-alternatives">
                          ({gap.alternatives.join(", ")})
                        </span>
                      {/if}
                    </div>
                  {/each}
                </div>
              {/if}
            </div>
          {/if}
        </div>

        <!-- Actions -->
        <div class="actions-section">
          <button class="btn btn-danger" on:click={handleDelete}>
            Delete Experiment
          </button>
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .detail-page {
    min-height: 100vh;
    background-color: var(--light-gray);
    padding: 2rem 0;
  }

  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
  }

  .detail-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }

  .detail-header h1 {
    margin: 0;
    font-size: 2rem;
    color: var(--primary-color);
  }

  .header-actions {
    display: flex;
    gap: 1rem;
  }

  .detail-content {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .summary-section {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid var(--light-gray);
  }

  .summary-card {
    background: var(--light-gray);
    padding: 1rem;
    border-radius: 4px;
  }

  .summary-card h3 {
    margin-top: 0;
    font-size: 0.9rem;
    color: var(--primary-color);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .summary-card p {
    margin: 0.5rem 0 0 0;
    font-size: 1.1rem;
    font-weight: 500;
  }

  .comparison-section,
  .results-section,
  .gaps-section {
    margin-bottom: 2rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid var(--light-gray);
  }

  .comparison-section h2,
  .results-section h2,
  .gaps-section h2 {
    font-size: 1.3rem;
    margin-bottom: 1rem;
    color: var(--primary-color);
  }

  .comparison-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }

  .stat-card {
    background: linear-gradient(135deg, #f8f9fa, #e9ecef);
    border: 1px solid var(--mid-gray);
    border-radius: 6px;
    padding: 1rem;
  }

  .stat-card h4 {
    margin-top: 0;
    margin-bottom: 0.75rem;
    color: var(--primary-color);
  }

  .stat {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  }

  .stat .label {
    font-size: 0.85rem;
    color: #666;
  }

  .stat .value {
    font-weight: 600;
    color: var(--accent-color);
  }

  .table-wrapper {
    overflow-x: auto;
  }

  .results-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
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
    max-width: 150px;
    word-break: break-word;
    font-size: 0.8rem;
  }

  .text-cell.filled {
    background: #e6f7e6;
    font-weight: 500;
  }

  .overall {
    font-weight: 600;
    color: var(--accent-color);
  }

  .gap-analysis {
    background: var(--light-gray);
    padding: 1rem;
    border-radius: 4px;
  }

  .gap-analysis p {
    margin: 0 0 1rem 0;
  }

  .gaps-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .gap-item {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    font-size: 0.9rem;
  }

  .gap-index {
    font-weight: 600;
    color: var(--accent-color);
    min-width: 30px;
  }

  .gap-choice {
    font-weight: 500;
    color: var(--primary-color);
  }

  .gap-alternatives {
    color: #999;
    font-size: 0.85rem;
  }

  .actions-section {
    display: flex;
    gap: 1rem;
    margin-top: 2rem;
  }

  .btn-danger {
    background: var(--danger);
    color: white;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
  }

  .btn-danger:hover {
    background: #c82828;
  }

  .loading {
    text-align: center;
    padding: 2rem;
    font-size: 1rem;
  }

  .error-message {
    background: #ffe6e6;
    color: var(--danger);
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1rem;
  }

  @media (max-width: 768px) {
    .detail-header {
      flex-direction: column;
      gap: 1rem;
      align-items: flex-start;
    }

    .header-actions {
      width: 100%;
    }

    .header-actions button {
      flex: 1;
    }

    .results-table {
      font-size: 0.75rem;
    }

    .results-table th,
    .results-table td {
      padding: 0.5rem;
    }

    .text-cell {
      max-width: 80px;
    }
  }
</style>
