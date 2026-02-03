<script>
  import { onMount } from 'svelte';
  import {
    getAvailableModels,
    createGapsInText,
    buildMCPRequest,
    callMCPService,
    saveResult,
    getSavedResults,
    getResultsByModel,
    deleteResult
  } from '../lib/gapGenerator.js';

  let bulkText = '';
  let removalPercent = 10;
  let selectedModel = '';
  let availableModels = [];
  let modelsLoading = true;
  let modelsError = '';
  let isProcessing = false;
  let error = '';
  let success = '';

  // Results display
  let originalText = '';
  let textWithGaps = '';
  let filledText = '';
  let gapsData = [];
  let processingTime = 0;
  let gapStats = { created: 0, total_words: 0 };
  let showResults = false;

  // Saved results
  let savedResults = [];
  let showSavedResults = false;

  onMount(async () => {
    // Load available models from Bielik
    try {
      const models = await getAvailableModels();
      availableModels = Array.isArray(models) ? models : [];
      console.log("Models loaded:", availableModels);
      
      if (availableModels.length > 0) {
        selectedModel = availableModels[0].name;
      } else {
        modelsError = "No models available";
      }
    } catch (err) {
      modelsError = `Failed to load models: ${err.message}`;
      console.error(err);
      // Use fallback models
      availableModels = [
        { name: "bielik-1.5b-gguf", type: "gguf", size: "1.7GB", polish_support: "excellent" },
        { name: "bielik-11b-gguf", type: "gguf", size: "7.2GB", polish_support: "excellent" },
        { name: "llama-3.1-8b", type: "inference_api", size: "8B", polish_support: "excellent" }
      ];
      selectedModel = availableModels[0].name;
    } finally {
      modelsLoading = false;
    }
    
    loadSavedResults();
  });

  function loadSavedResults() {
    savedResults = getSavedResults();
  }

  async function handleProcess() {
    error = '';
    success = '';
    isProcessing = true;
    showResults = false;

    try {
      // Validate input
      if (!bulkText.trim()) {
        throw new Error('Please paste bulk text');
      }

      if (bulkText.trim().length < 100) {
        throw new Error('Text too short (minimum 100 chars)');
      }

      // Step 1: Create gaps
      console.log('Step 1: Creating gaps...');
      const gapResult = createGapsInText(bulkText, removalPercent);

      originalText = bulkText;
      textWithGaps = gapResult.text_with_gaps;
      gapStats = {
        created: gapResult.gaps_created,
        total_words: gapResult.word_count
      };

      // Step 2: Build MCP request
      console.log('Step 2: Building MCP request...');
      const mcpRequest = buildMCPRequest(textWithGaps, selectedModel);

      // Step 3: Call MCP service
      console.log('Step 3: Calling MCP service...');
      const mcpResult = await callMCPService(mcpRequest);

      filledText = mcpResult.filled_text;
      gapsData = mcpResult.gaps || [];
      processingTime = mcpResult.processing_time_ms;

      // Step 4: Save result
      console.log('Step 4: Saving result...');
      const savedId = saveResult({
        model: selectedModel,
        original_text: originalText,
        text_with_gaps: textWithGaps,
        filled_text: filledText,
        gaps_data: gapsData,
        gaps_count: gapStats.created,
        total_words: gapStats.total_words,
        removal_percent: removalPercent,
        processing_time_ms: processingTime,
        status: 'success'
      });

      success = `✅ Gap-filling complete! Result saved. (${gapStats.created} gaps, ${processingTime}ms)`;
      showResults = true;
      loadSavedResults();
    } catch (err) {
      console.error('Error:', err);
      error = `❌ ${err.message}`;
    } finally {
      isProcessing = false;
    }
  }

  function handleDeleteResult(resultId) {
    if (confirm('Delete this result?')) {
      deleteResult(resultId);
      loadSavedResults();
    }
  }

  function viewResult(result) {
    originalText = result.original_text;
    textWithGaps = result.text_with_gaps;
    filledText = result.filled_text;
    gapsData = result.gaps_data;
    processingTime = result.processing_time_ms;
    gapStats = {
      created: result.gaps_count,
      total_words: result.total_words
    };
    selectedModel = result.model;
    showResults = true;
    showSavedResults = false;
  }

  function downloadResult() {
    const data = {
      model: selectedModel,
      original_text: originalText,
      text_with_gaps: textWithGaps,
      filled_text: filledText,
      gaps: gapsData,
      timestamp: new Date().toISOString()
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bulk-gaps-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }
</script>

<div class="bulk-gaps-container">
  <h1>🚗 Bulk Ad Gap-Filling</h1>
  <p class="subtitle">Upload 50+ ads, remove random words, fill with AI</p>

  <div class="main-panel">
    <div class="input-section">
      <h2>Step 1: Paste Your Ads</h2>
      <textarea
        bind:value={bulkText}
        placeholder="Paste 50+ concatenated car ads here..."
        rows="10"
      />

      <h2>Step 2: Configure</h2>
      <div class="config-row">
        <div class="config-item">
          <label>Words to remove: <strong>{removalPercent}%</strong></label>
          <input
            type="range"
            bind:value={removalPercent}
            min="5"
            max="50"
            step="5"
            disabled={isProcessing}
          />
        </div>

        <div class="config-item">
          <label>Model:</label>
          {#if modelsLoading}
            <select disabled>
              <option>Loading models...</option>
            </select>
          {:else if modelsError}
            <select disabled>
              <option>Error: {modelsError}</option>
            </select>
          {:else}
            <select bind:value={selectedModel} disabled={isProcessing}>
              {#each availableModels as model}
                <option value={model.name}>
                  {model.name} ({model.type}, {model.size})
                </option>
              {/each}
            </select>
          {/if}
        </div>
      </div>

      <button
        on:click={handleProcess}
        disabled={isProcessing || !bulkText.trim()}
        class:processing={isProcessing}
      >
        {#if isProcessing}
          ⏳ Processing...
        {:else}
          🎯 Create Gaps & Fill
        {/if}
      </button>
    </div>

    {#if error}
      <div class="error-message">{error}</div>
    {/if}

    {#if success}
      <div class="success-message">{success}</div>
    {/if}

    {#if showResults}
      <div class="results-section">
        <h2>Results</h2>

        <div class="stats">
          <div class="stat">
            <span class="label">Gaps Created:</span>
            <span class="value">{gapStats.created}</span>
          </div>
          <div class="stat">
            <span class="label">Total Words:</span>
            <span class="value">{gapStats.total_words}</span>
          </div>
          <div class="stat">
            <span class="label">Processing Time:</span>
            <span class="value">{processingTime}ms</span>
          </div>
          <div class="stat">
            <span class="label">Model:</span>
            <span class="value">{selectedModel}</span>
          </div>
        </div>

        <div class="comparison">
          <div class="column">
            <h3>Original Text</h3>
            <div class="text-box">{originalText}</div>
          </div>

          <div class="column">
            <h3>With Gaps</h3>
            <div class="text-box highlight-gaps">{@html textWithGaps.replace(/\[GAP:\d+\]/g, m => `<span class="gap">${m}</span>`)}</div>
          </div>

          <div class="column">
            <h3>Filled Text</h3>
            <div class="text-box filled">{filledText}</div>
          </div>
        </div>

        <div class="gaps-list">
          <h3>Gaps Filled ({gapsData.length})</h3>
          <div class="gaps">
            {#each gapsData as gap}
              <div class="gap-item">
                <span class="index">[GAP:{gap.index}]</span>
                <span class="choice">→ {gap.choice}</span>
              </div>
            {/each}
          </div>
        </div>

        <button on:click={downloadResult} class="download-btn">
          ⬇️ Download JSON
        </button>
      </div>
    {/if}

    <div class="saved-section">
      <button on:click={() => (showSavedResults = !showSavedResults)} class="toggle-btn">
        {showSavedResults ? '▼' : '▶'} Saved Results ({savedResults.length})
      </button>

      {#if showSavedResults}
        <div class="saved-list">
          {#if savedResults.length === 0}
            <p class="no-results">No saved results yet</p>
          {:else}
            {#each savedResults as result}
              <div class="result-item">
                <div class="result-header">
                  <span class="model">{result.model}</span>
                  <span class="timestamp">{new Date(result.timestamp).toLocaleString()}</span>
                  <span class="gaps-count">{result.gaps_count} gaps</span>
                </div>
                <div class="result-actions">
                  <button on:click={() => viewResult(result)} class="view-btn">View</button>
                  <button
                    on:click={() => handleDeleteResult(result.id)}
                    class="delete-btn"
                  >
                    Delete
                  </button>
                </div>
              </div>
            {/each}
          {/if}
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .bulk-gaps-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }

  h1 {
    color: #333;
    margin-bottom: 5px;
  }

  .subtitle {
    color: #666;
    margin-bottom: 30px;
  }

  .main-panel {
    background: #f9f9f9;
    border-radius: 8px;
    padding: 20px;
  }

  h2 {
    margin-top: 20px;
    margin-bottom: 15px;
    color: #333;
    font-size: 18px;
  }

  textarea {
    width: 100%;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-family: monospace;
    font-size: 14px;
    resize: vertical;
  }

  .config-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 20px;
  }

  .config-item {
    display: flex;
    flex-direction: column;
  }

  .config-item label {
    margin-bottom: 8px;
    color: #333;
    font-weight: 500;
  }

  input[type='range'] {
    height: 6px;
    border-radius: 3px;
  }

  select {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
  }

  button {
    padding: 12px 24px;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s;
  }

  button:hover:not(:disabled) {
    background: #0056b3;
  }

  button:disabled {
    background: #ccc;
    cursor: not-allowed;
  }

  button.processing {
    background: #ffc107;
  }

  .error-message {
    background: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
    padding: 12px;
    border-radius: 4px;
    margin: 20px 0;
  }

  .success-message {
    background: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
    padding: 12px;
    border-radius: 4px;
    margin: 20px 0;
  }

  .results-section {
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #ddd;
  }

  .stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-bottom: 20px;
  }

  .stat {
    background: white;
    padding: 12px;
    border-radius: 4px;
    border: 1px solid #ddd;
  }

  .stat .label {
    display: block;
    color: #666;
    font-size: 12px;
    margin-bottom: 4px;
  }

  .stat .value {
    display: block;
    color: #007bff;
    font-size: 24px;
    font-weight: bold;
  }

  .comparison {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin-bottom: 20px;
  }

  .column h3 {
    margin-bottom: 10px;
    color: #333;
    font-size: 14px;
  }

  .text-box {
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 12px;
    height: 200px;
    overflow-y: auto;
    font-size: 12px;
    line-height: 1.6;
    white-space: pre-wrap;
    word-wrap: break-word;
  }

  .text-box.highlight-gaps {
    background: #fffacd;
  }

  .text-box.filled {
    background: #f0fff0;
  }

  .gap {
    background: #ffeb3b;
    color: #333;
    padding: 2px 4px;
    border-radius: 2px;
    font-weight: bold;
  }

  .gaps-list {
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 12px;
    margin-bottom: 20px;
  }

  .gaps {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 10px;
  }

  .gap-item {
    background: #f5f5f5;
    padding: 8px;
    border-radius: 4px;
    font-size: 12px;
  }

  .gap-item .index {
    color: #666;
    font-weight: bold;
  }

  .gap-item .choice {
    color: #007bff;
    margin-left: 5px;
  }

  .download-btn {
    background: #28a745;
    margin-top: 15px;
  }

  .download-btn:hover {
    background: #218838;
  }

  .saved-section {
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #ddd;
  }

  .toggle-btn {
    background: #6c757d;
    width: 100%;
    text-align: left;
  }

  .toggle-btn:hover {
    background: #5a6268;
  }

  .saved-list {
    margin-top: 15px;
  }

  .no-results {
    color: #999;
    text-align: center;
    padding: 20px;
  }

  .result-item {
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 12px;
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .result-header {
    flex: 1;
  }

  .model {
    background: #e3f2fd;
    color: #1976d2;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 12px;
    font-weight: bold;
    margin-right: 10px;
  }

  .timestamp {
    color: #666;
    font-size: 12px;
    margin-right: 10px;
  }

  .gaps-count {
    color: #28a745;
    font-weight: bold;
    font-size: 12px;
  }

  .result-actions {
    display: flex;
    gap: 5px;
  }

  .view-btn {
    background: #007bff;
    padding: 6px 12px;
    font-size: 12px;
  }

  .delete-btn {
    background: #dc3545;
    padding: 6px 12px;
    font-size: 12px;
  }

  .delete-btn:hover {
    background: #c82333;
  }

  @media (max-width: 1024px) {
    .comparison {
      grid-template-columns: 1fr;
    }

    .config-row {
      grid-template-columns: 1fr;
    }

    .stats {
      grid-template-columns: repeat(2, 1fr);
    }
  }
</style>
