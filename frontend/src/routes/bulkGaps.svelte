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
    deleteResult,
    loadBulkAds
  } from '../lib/gapGenerator.js';

  let bulkText = '';
  let removalPercent = 10;
  let temperature = 0.3;
  let selectedModel = '';
  let availableModels = [];
  let modelsLoading = true;
  let modelsError = '';
  let isProcessing = false;
  let error = '';
  let success = '';

  // Bulk ads loading
  let adCount = 50;
  let isLoadingAds = false;

  // Results display
  let originalText = '';
  let textWithGaps = '';
  let filledText = '';
  let gapsData = [];
  let processingTime = 0;
  let gapStats = { created: 0, total_words: 0 };
  let showResults = false;
  let gapOriginalsMap = {};

  // Multi-model testing
  let gapsAreActive = false; // Track if gaps have been created and are ready for testing
  let modelTestResults = []; // Array of results from different models tested on same gaps
  let currentTestingModel = ''; // Model being tested in the multi-model phase
  let isTestingModel = false; // Flag for testing with a new model
  let testError = '';

  // Saved results
  let savedResults = [];
  let showSavedResults = false;
  let sortBy = 'recent'; // 'recent', 'model', 'gaps'
  let filterModel = ''; // Filter by model
  let groupedResults = {}; // Group results by gap configuration

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
        { name: "bielik-1.5b-transformer", type: "transformer", size: "2.4GB", polish_support: "excellent" },
        { name: "bielik-11b-transformer", type: "transformer", size: "22GB", polish_support: "excellent" },
        { name: "llama-3.1-8b", type: "inference_api", size: "8B", polish_support: "excellent" }
      ];
      selectedModel = availableModels[0].name;
    } finally {
      modelsLoading = false;
    }
    
    loadSavedResults();
  });

  function highlightFilledWords(text, gaps) {
    if (!text || !gaps || gaps.length === 0) return text;

    let result = text;
    // Create a map to track count of each word to bold (for multiple occurrences)
    const wordCounts = {};
    gaps.forEach(gap => {
      wordCounts[gap.choice] = (wordCounts[gap.choice] || 0) + 1;
    });

    // For each unique filled word, bold only the required number of occurrences
    Object.entries(wordCounts).forEach(([word, count]) => {
      let replacements = 0;
      // Use a function in replace to limit replacements per word
      const regex = new RegExp(`\\b${word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'gi');
      result = result.replace(regex, (match) => {
        if (replacements < count) {
          replacements++;
          return `<strong>${match}</strong>`;
        }
        return match;
      });
    });

    return result;
  }

  function loadSavedResults() {
    savedResults = getSavedResults();
    groupResultsByConfiguration();
  }

  function groupResultsByConfiguration() {
    groupedResults = {};
    
    savedResults.forEach(result => {
      // Create a key from the gap configuration
      const key = result.text_with_gaps || 'ungrouped';
      const hash = key.substring(0, 50); // Use first 50 chars as identifier
      
      if (!groupedResults[hash]) {
        groupedResults[hash] = {
          gaps_count: result.gaps_count,
          total_words: result.total_words,
          created_at: result.timestamp,
          results: []
        };
      }
      
      groupedResults[hash].results.push(result);
    });

    // Sort results within each group by model name
    Object.keys(groupedResults).forEach(key => {
      groupedResults[key].results.sort((a, b) => a.model.localeCompare(b.model));
    });
  }

  function getUniqueModels() {
    const models = new Set(savedResults.map(r => r.model));
    return Array.from(models).sort();
  }

  function getSortedGroups() {
    const groups = Object.entries(groupedResults);
    
    if (sortBy === 'recent') {
      groups.sort((a, b) => new Date(b[1].created_at) - new Date(a[1].created_at));
    } else if (sortBy === 'gaps') {
      groups.sort((a, b) => b[1].gaps_count - a[1].gaps_count);
    }
    
    return groups;
  }

  function getFilteredResults(results) {
    if (!filterModel) return results;
    return results.filter(r => r.model === filterModel);
  }

  function compareResults(groupKey) {
    // Load all results from this group to compare
    const group = groupedResults[groupKey];
    if (group.results.length === 0) return;
    
    // Set the original text and gaps from first result
    const firstResult = group.results[0];
    originalText = firstResult.original_text;
    textWithGaps = firstResult.text_with_gaps;
    gapStats = {
      created: firstResult.gaps_count,
      total_words: firstResult.total_words
    };
    
    // Load all model results from this group for comparison
    modelTestResults = group.results.map(r => ({
      model: r.model,
      filled_text: r.filled_text,
      gaps: r.gaps_data,
      processing_time_ms: r.processing_time_ms,
      timestamp: r.timestamp
    }));
    
    gapsAreActive = false;
    showResults = true;
    showSavedResults = false;
  }

  async function handleLoadAds() {
    error = '';
    success = '';
    isLoadingAds = true;

    try {
      if (adCount < 1 || adCount > 500) {
        throw new Error('Ad count must be between 1 and 500');
      }

      console.log(`Loading ${adCount} ads from retrieval service...`);
      const result = await loadBulkAds(adCount, true);
      
      bulkText = result.bulk_text;
      success = `✅ Loaded ${result.count} ads (${bulkText.length} characters)`;
    } catch (err) {
      console.error('Error loading ads:', err);
      error = `❌ Failed to load ads: ${err.message}`;
    } finally {
      isLoadingAds = false;
    }
  }

  async function handleProcess() {
    error = '';
    success = '';
    isProcessing = true;
    showResults = false;
    gapsAreActive = false;
    modelTestResults = [];

    try {
      // Validate input
      if (!bulkText.trim()) {
        throw new Error('Please paste bulk text');
      }

      if (bulkText.trim().length < 100) {
        throw new Error('Text too short (minimum 100 chars)');
      }

      // Step 1: Create gaps (only this step now)
      console.log('Step 1: Creating gaps...');
      const gapResult = createGapsInText(bulkText, removalPercent);

      originalText = bulkText;
      textWithGaps = gapResult.text_with_gaps;
      gapStats = {
        created: gapResult.gaps_created,
        total_words: gapResult.word_count
      };
      gapOriginalsMap = (gapResult.gap_originals || []).reduce((acc, gap) => {
        acc[gap.index] = gap.original;
        return acc;
      }, {});

      success = `✅ Gaps created! (${gapStats.created} gaps out of ${gapStats.total_words} words). Now select a model and test.`;
      gapsAreActive = true;
      showResults = true;
      modelTestResults = [];
      currentTestingModel = selectedModel;
    } catch (err) {
      console.error('Error:', err);
      error = `❌ ${err.message}`;
    } finally {
      isProcessing = false;
    }
  }

  async function handleTestWithModel() {
    testError = '';
    error = '';
    isTestingModel = true;

    try {
      if (!textWithGaps) {
        throw new Error('Please create gaps first');
      }

      if (!currentTestingModel) {
        throw new Error('Please select a model');
      }

      console.log(`Testing with model: ${currentTestingModel}`);

      // Check if this model has already been tested
      const alreadyTested = modelTestResults.find(r => r.model === currentTestingModel);
      if (alreadyTested) {
        throw new Error(`Model "${currentTestingModel}" has already been tested. Select a different model.`);
      }

      // Build MCP request
      const mcpRequest = buildMCPRequest(textWithGaps, currentTestingModel, temperature);

      // Call MCP service
      const mcpResult = await callMCPService(mcpRequest);

      // Enrich gaps with original words (MCP service should return these)
      const enrichedGaps = (mcpResult.gaps || []).map(gap => ({
        ...gap,
        original: gapOriginalsMap[gap.index] || gap.original || gap.original_word || '—'
      }));

      // Store result
      const testResult = {
        model: currentTestingModel,
        filled_text: mcpResult.filled_text,
        gaps: enrichedGaps,
        processing_time_ms: mcpResult.processing_time_ms,
        timestamp: new Date().toISOString()
      };

      modelTestResults = [...modelTestResults, testResult];

      success = `✅ Tested with ${currentTestingModel}! (${mcpResult.processing_time_ms}ms). Select another model to compare.`;

      // Save this result
      saveResult({
        model: currentTestingModel,
        original_text: originalText,
        text_with_gaps: textWithGaps,
        filled_text: testResult.filled_text,
        gaps_data: testResult.gaps,
        gaps_count: gapStats.created,
        total_words: gapStats.total_words,
        removal_percent: removalPercent,
        processing_time_ms: testResult.processing_time_ms,
        status: 'success'
      });

      // Auto-select first untested model or reset
      const nextAvailableModel = availableModels.find(m => !modelTestResults.find(r => r.model === m.name));
      currentTestingModel = nextAvailableModel ? nextAvailableModel.name : '';

      loadSavedResults();
    } catch (err) {
      console.error('Error:', err);
      testError = `❌ ${err.message}`;
    } finally {
      isTestingModel = false;
    }
  }

  function regenerateGaps() {
    gapsAreActive = false;
    modelTestResults = [];
    gapOriginalsMap = {};
    showResults = false;
    success = '';
    //Re-run the process function
    handleProcess();
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
      gap_configuration: {
        original_text: originalText,
        text_with_gaps: textWithGaps,
        gaps_count: gapStats.created,
        total_words: gapStats.total_words,
        removal_percent: removalPercent,
        created_at: new Date().toISOString()
      },
      model_results: modelTestResults.map(result => ({
        model: result.model,
        filled_text: result.filled_text,
        gaps: result.gaps.map(gap => ({
          index: gap.index,
          original: gap.original,
          choice: gap.choice
        })),
        processing_time_ms: result.processing_time_ms,
        tested_at: result.timestamp
      }))
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bulk-gaps-comparison-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function downloadModelResult(result) {
    const data = {
      gap_configuration: {
        original_text: originalText,
        text_with_gaps: textWithGaps,
        gaps_count: gapStats.created,
        total_words: gapStats.total_words,
        removal_percent: removalPercent
      },
      model_result: {
        model: result.model,
        filled_text: result.filled_text,
        gaps: result.gaps.map(gap => ({
          index: gap.index,
          original: gap.original,
          choice: gap.choice
        })),
        processing_time_ms: result.processing_time_ms,
        tested_at: result.timestamp
      }
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `gap-filling-${result.model.replace(/\s+/g, '-')}-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function downloadSavedResult(result) {
    const data = {
      gap_configuration: {
        original_text: result.original_text,
        text_with_gaps: result.text_with_gaps,
        gaps_count: result.gaps_count,
        total_words: result.total_words,
        removal_percent: result.removal_percent
      },
      model_result: {
        model: result.model,
        filled_text: result.filled_text,
        gaps: (result.gaps_data || []).map(gap => ({
          index: gap.index,
          original: gap.original,
          choice: gap.choice
        })),
        processing_time_ms: result.processing_time_ms,
        tested_at: result.timestamp
      }
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `gap-filling-${result.model.replace(/\s+/g, '-')}-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }
</script>

<div class="bulk-gaps-container">
  <h1>🚗 Bulk Ad Gap-Filling</h1>
  <p class="subtitle">Upload 50+ ads, remove random words, fill with AI</p>

  <div class="main-panel">
    <div class="input-section">
      <h2>Step 1: Load or Paste Your Ads</h2>
      
      <div class="load-ads-section">
        <div class="load-ads-group">
          <label>Load from database:</label>
          <div class="load-row">
            <input
              type="number"
              bind:value={adCount}
              min="1"
              max="500"
              disabled={isLoadingAds}
              placeholder="50"
            />
            <button
              on:click={handleLoadAds}
              disabled={isLoadingAds || adCount < 1}
              class:loading={isLoadingAds}
            >
              {#if isLoadingAds}
                ⏳ Loading...
              {:else}
                🪄 Load Bulk Ads
              {/if}
            </button>
          </div>
        </div>
        <p class="hint">or paste ads manually below</p>
      </div>

      <textarea
        bind:value={bulkText}
        placeholder="Paste 50+ concatenated car ads here, or click 'Load Bulk Ads' above..."
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
      </div>

      <button
        on:click={handleProcess}
        disabled={isProcessing || !bulkText.trim()}
        class:processing={isProcessing}
      >
        {#if isProcessing}
          ⏳ Creating Gaps...
        {:else}
          🎯 Create Gaps
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
            <span class="label">Models Tested:</span>
            <span class="value">{modelTestResults.length}</span>
          </div>
          <div class="stat">
            <span class="label">Removal %:</span>
            <span class="value">{removalPercent}%</span>
          </div>
        </div>

        <div class="comparison">
          <div class="column">
            <h3>Original Text</h3>
            <div class="text-box">{originalText}</div>
          </div>

          <div class="column">
            <h3>Text with Gaps</h3>
            <div class="text-box highlight-gaps">{@html textWithGaps.replace(/\[GAP:\d+\]/g, m => `<span class="gap">${m}</span>`)}</div>
          </div>
        </div>

        {#if gapsAreActive}
          <div class="model-testing-section">
            <h3>🧪 Test with Models</h3>
            <p class="testing-info">The gaps above are locked. Test them with different models to compare results.</p>

            <div class="model-test-controls">
              <div class="control-item">
                <label>Select Model:</label>
                {#if modelsLoading}
                  <select disabled>
                    <option>Loading models...</option>
                  </select>
                {:else if modelsError}
                  <select disabled>
                    <option>Error: {modelsError}</option>
                  </select>
                {:else}
                  <select bind:value={currentTestingModel} disabled={isTestingModel}>
                    {#each availableModels as model}
                      {#if !modelTestResults.find(r => r.model === model.name)}
                        <option value={model.name}>
                          {model.name} ({model.type}, {model.size})
                        </option>
                      {/if}
                    {/each}
                  </select>
                {/if}
              </div>

              <div class="control-item">
                <label>Temperature: <strong>{temperature.toFixed(1)}</strong></label>
                <input
                  type="range"
                  bind:value={temperature}
                  min="0.0"
                  max="1.0"
                  step="0.1"
                  disabled={isTestingModel}
                />
                <p class="slider-hint">Conservative (0.0) → Creative (1.0)</p>
              </div>

              <button
                on:click={handleTestWithModel}
                disabled={isTestingModel || !currentTestingModel}
                class:testing={isTestingModel}
              >
                {#if isTestingModel}
                  ⏳ Testing...
                {:else}
                  📤 Send to Model
                {/if}
              </button>

              <button
                on:click={regenerateGaps}
                disabled={isProcessing || isTestingModel}
                class="regenerate-btn"
              >
                🔄 Regenerate Gaps
              </button>
            </div>

            {#if testError}
              <div class="error-message">{testError}</div>
            {/if}

            {#if modelTestResults.length > 0}
              <div class="model-results">
                <h4>Results from {modelTestResults.length} Model(s)</h4>
                
                {#each modelTestResults as result, idx}
                  <div class="model-result-item">
                    <div class="result-header">
                      <span class="model-badge">{result.model}</span>
                      <span class="timing">{result.processing_time_ms}ms</span>
                      <span class="timestamp">{new Date(result.timestamp).toLocaleTimeString()}</span>
                    </div>
                    
                    <div class="filled-text-display">
                      <strong>Filled Text:</strong>
                      <div class="text-box">{@html highlightFilledWords(result.filled_text, result.gaps)}</div>
                    </div>

                    <div class="gaps-filled">
                      <strong>All Gaps Filled ({result.gaps.length}):</strong>
                      <div class="gaps-table">
                        <div class="gaps-header">
                          <span class="col-index">Gap</span>
                          <span class="col-original">Original</span>
                          <span class="col-filled">Filled by {result.model}</span>
                        </div>
                        {#each result.gaps as gap}
                          <div class="gaps-row">
                            <span class="col-index">[{gap.index}]</span>
                            <span class="col-original">{gap.original || '—'}</span>
                            <span class="col-filled"><strong>{gap.choice}</strong></span>
                          </div>
                        {/each}
                      </div>
                    </div>

                    <div class="result-download">
                      <button on:click={() => downloadModelResult(result)} class="download-model-btn">
                        ⬇️ Download JSON
                      </button>
                    </div>
                  </div>
                {/each}
              </div>
            {/if}
          </div>
        {/if}

        {#if !gapsAreActive && modelTestResults.length === 0}
          <button on:click={downloadResult} class="download-btn" style="width: 100%;">
            ⬇️ Download Gaps Configuration
          </button>
        {/if}
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
            <div class="results-controls">
              <div class="control-group">
                <label>Sort by:</label>
                <select bind:value={sortBy}>
                  <option value="recent">Most Recent</option>
                  <option value="gaps">Most Gaps</option>
                </select>
              </div>

              <div class="control-group">
                <label>Filter by model:</label>
                <select bind:value={filterModel}>
                  <option value="">All Models</option>
                  {#each getUniqueModels() as model}
                    <option value={model}>{model}</option>
                  {/each}
                </select>
              </div>
            </div>

            <div class="grouped-results">
              {#each getSortedGroups() as [groupKey, group]}
                <div class="result-group">
                  <div class="group-header">
                    <div class="group-info">
                      <h4>Gap Configuration</h4>
                      <div class="group-stats">
                        <span class="stat-badge">
                          <strong>{group.gaps_count}</strong> gaps
                        </span>
                        <span class="stat-badge">
                          <strong>{group.total_words}</strong> words
                        </span>
                        <span class="stat-badge">
                          <strong>{group.results.length}</strong> model{group.results.length !== 1 ? 's' : ''}
                        </span>
                      </div>
                      <div class="group-models">
                        {#each group.results as result}
                          <span class="model-pill">{result.model}</span>
                        {/each}
                      </div>
                    </div>
                    <div class="group-actions">
                      {#if group.results.length > 1}
                        <button
                          on:click={() => compareResults(groupKey)}
                          class="compare-btn"
                          title="Compare all models from this configuration"
                        >
                          🔀 Compare All
                        </button>
                      {/if}
                    </div>
                  </div>

                  <div class="group-results">
                    {#each getFilteredResults(group.results) as result}
                      <div class="result-item-detailed">
                        <div class="result-model-row">
                          <span class="model-badge-large">{result.model}</span>
                          <span class="result-time">{new Date(result.timestamp).toLocaleString()}</span>
                          <span class="result-timing">{result.processing_time_ms}ms</span>
                        </div>

                        <div class="result-preview">
                          <strong>Filled Text Preview:</strong>
                          <div class="text-preview">
                            {result.filled_text.substring(0, 150)}{result.filled_text.length > 150 ? '...' : ''}
                          </div>
                        </div>

                        <div class="result-item-actions">
                          <button on:click={() => viewResult(result)} class="view-btn">👁️ View Full</button>
                          <button on:click={() => downloadSavedResult(result)} class="download-btn-small">⬇️ JSON</button>
                          <button on:click={() => handleDeleteResult(result.id)} class="delete-btn">🗑️ Delete</button>
                        </div>
                      </div>
                    {/each}
                    {#if filterModel && getFilteredResults(group.results).length === 0}
                      <p class="no-filter-results">No results for {filterModel}</p>
                    {/if}
                  </div>
                </div>
              {/each}
            </div>
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

  .load-ads-section {
    background: #e3f2fd;
    border: 1px solid #90caf9;
    border-radius: 4px;
    padding: 15px;
    margin-bottom: 15px;
  }

  .load-ads-group {
    margin-bottom: 8px;
  }

  .load-ads-group label {
    display: block;
    margin-bottom: 8px;
    color: #333;
    font-weight: 500;
  }

  .load-row {
    display: flex;
    gap: 10px;
  }

  .load-row input[type='number'] {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    width: 100px;
  }

  .load-row button {
    padding: 8px 16px;
    background: #2196f3;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.3s;
    font-weight: 500;
  }

  .load-row button:hover:not(:disabled) {
    background: #1976d2;
  }

  .load-row button:disabled {
    background: #ccc;
    cursor: not-allowed;
  }

  .load-row button.loading {
    background: #ffc107;
  }

  .hint {
    color: #666;
    font-size: 12px;
    margin: 8px 0 0 0;
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
  .slider-hint {    font-size: 12px;    color: #666;    margin: 6px 0 0 0;  }

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

  .results-controls {
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
    padding: 15px;
    background: #f5f5f5;
    border-radius: 6px;
  }

  .control-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
    flex: 1;
  }

  .control-group label {
    font-weight: 500;
    color: #333;
    font-size: 13px;
  }

  .control-group select {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 13px;
    background: white;
  }

  .no-results {
    color: #999;
    text-align: center;
    padding: 20px;
  }

  .grouped-results {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }

  .result-group {
    background: white;
    border: 1px solid #ddd;
    border-radius: 6px;
    overflow: hidden;
  }

  .group-header {
    background: #f8f9fa;
    border-bottom: 2px solid #e9ecef;
    padding: 15px;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 15px;
  }

  .group-info {
    flex: 1;
  }

  .group-info h4 {
    margin: 0 0 10px 0;
    color: #333;
    font-size: 14px;
  }

  .group-stats {
    display: flex;
    gap: 10px;
    margin-bottom: 10px;
    flex-wrap: wrap;
  }

  .stat-badge {
    background: #e7f3ff;
    color: #0066cc;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
  }

  .group-models {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .model-pill {
    background: #f0f0f0;
    color: #333;
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 12px;
    border: 1px solid #ddd;
  }

  .group-actions {
    display: flex;
    gap: 10px;
  }

  .compare-btn {
    background: #6c63ff;
    color: white;
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.3s;
    font-weight: 500;
  }

  .compare-btn:hover {
    background: #5a52d5;
  }

  .group-results {
    padding: 10px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .result-item-detailed {
    background: #fafafa;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 12px;
    transition: all 0.2s;
  }

  .result-item-detailed:hover {
    background: #f5f5f5;
    border-color: #b0b0b0;
  }

  .result-model-row {
    display: flex;
    gap: 12px;
    align-items: center;
    margin-bottom: 10px;
    flex-wrap: wrap;
  }

  .model-badge-large {
    background: #2196f3;
    color: white;
    padding: 4px 12px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 12px;
  }

  .result-time {
    color: #666;
    font-size: 12px;
  }

  .result-timing {
    background: #fff3cd;
    color: #856404;
    padding: 2px 8px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: 500;
  }

  .result-preview {
    margin-bottom: 10px;
  }

  .result-preview strong {
    display: block;
    color: #333;
    font-size: 12px;
    margin-bottom: 6px;
  }

  .text-preview {
    background: white;
    border: 1px solid #ddd;
    border-radius: 3px;
    padding: 8px;
    font-size: 11px;
    line-height: 1.4;
    color: #555;
    max-height: 60px;
    overflow-y: auto;
    word-break: break-word;
  }

  .result-item-actions {
    display: flex;
    gap: 6px;
  }

  .view-btn {
    background: #007bff;
    color: white;
    padding: 6px 12px;
    border: none;
    border-radius: 3px;
    font-size: 11px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .view-btn:hover {
    background: #0056b3;
  }

  .delete-btn {
    background: #dc3545;
    color: white;
    padding: 6px 12px;
    border: none;
    border-radius: 3px;
    font-size: 11px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .delete-btn:hover {
    background: #c82333;
  }

  .download-btn-small {
    background: #28a745;
    color: white;
    padding: 6px 12px;
    border: none;
    border-radius: 3px;
    font-size: 11px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .download-btn-small:hover {
    background: #218838;
  }

  .result-download {
    margin-top: 12px;
    border-top: 1px solid #e0e0e0;
    padding-top: 12px;
  }

  .download-model-btn {
    background: #28a745;
    color: white;
    padding: 8px 16px;
    border: none;
    border-radius: 3px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.2s;
    width: 100%;
  }

  .download-model-btn:hover {
    background: #218838;
  }

  .no-filter-results {
    color: #999;
    font-size: 12px;
    text-align: center;
    padding: 12px;
  }

  .model-testing-section {
    background: #f0f7ff;
    border: 2px solid #2196f3;
    border-radius: 8px;
    padding: 20px;
    margin-top: 20px;
  }

  .model-testing-section h3 {
    color: #1976d2;
    margin-top: 0;
  }

  .testing-info {
    color: #1565c0;
    font-size: 14px;
    margin: 10px 0 20px 0;
    padding: 10px;
    background: #e3f2fd;
    border-left: 3px solid #2196f3;
    border-radius: 3px;
  }

  .model-test-controls {
    display: grid;
    grid-template-columns: 1fr 1fr auto auto;
    gap: 15px;
    margin-bottom: 20px;
    align-items: flex-end;
  }

  .control-item {
    display: flex;
    flex-direction: column;
  }

  .control-item label {
    margin-bottom: 8px;
    color: #333;
    font-weight: 500;
    font-size: 14px;
  }

  .control-item select {
    padding: 10px;
    border: 1px solid #2196f3;
    border-radius: 4px;
    font-size: 14px;
  }

  .control-item input[type='range'] {
    margin-bottom: 6px;
  }

  .model-test-controls button {
    padding: 10px 16px;
    font-size: 14px;
    height: fit-content;
  }

  .model-test-controls button.testing {
    background: #ffc107;
  }

  .regenerate-btn {
    background: #ff9800 !important;
  }

  .regenerate-btn:hover {
    background: #f57c00 !important;
  }

  .model-results {
    margin-top: 20px;
    padding-top: 20px;
    border-top: 2px solid #2196f3;
  }

  .model-results h4 {
    color: #1976d2;
    margin-bottom: 15px;
  }

  .model-result-item {
    background: white;
    border: 1px solid #90caf9;
    border-radius: 6px;
    padding: 15px;
    margin-bottom: 15px;
  }

  .model-result-item .result-header {
    display: flex;
    gap: 12px;
    align-items: center;
    margin-bottom: 12px;
    flex-wrap: wrap;
  }

  .model-badge {
    background: #2196f3;
    color: white;
    padding: 4px 10px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 12px;
  }

  .timing {
    color: #666;
    font-size: 12px;
    background: #f5f5f5;
    padding: 4px 8px;
    border-radius: 3px;
  }

  .filled-text-display {
    margin-bottom: 12px;
  }

  .filled-text-display strong {
    display: block;
    margin-bottom: 8px;
    color: #333;
  }

  .filled-text-display .text-box {
    background: #f0fff0;
    height: 120px;
  }

  .filled-text-display strong {
    color: #d32f2f;
    background: #ffebee;
    padding: 1px 3px;
    border-radius: 2px;
    font-weight: 700;
  }

  .gaps-filled {
    margin-top: 12px;
  }

  .gaps-filled strong {
    display: block;
    margin-bottom: 8px;
    color: #333;
  }

  .gaps-table {
    border: 1px solid #ddd;
    border-radius: 4px;
    overflow: hidden;
    background: white;
    max-height: 300px;
    overflow-y: auto;
  }

  .gaps-header {
    display: grid;
    grid-template-columns: 80px 1fr 1fr;
    background: #f0f0f0;
    border-bottom: 2px solid #ddd;
    padding: 8px;
    font-weight: bold;
    font-size: 11px;
    position: sticky;
    top: 0;
    gap: 8px;
  }

  .gaps-row {
    display: grid;
    grid-template-columns: 80px 1fr 1fr;
    padding: 8px;
    border-bottom: 1px solid #f0f0f0;
    font-size: 11px;
    gap: 8px;
    align-items: center;
  }

  .gaps-row:hover {
    background: #f9f9f9;
  }

  .col-index {
    font-weight: bold;
    color: #f57c00;
    white-space: nowrap;
  }

  .col-original {
    color: #666;
    background: #fffacd;
    padding: 4px;
    border-radius: 2px;
    word-break: break-word;
  }

  .col-filled {
    color: #1976d2;
    background: #e3f2fd;
    padding: 4px;
    border-radius: 2px;
    word-break: break-word;
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

    .model-test-controls {
      grid-template-columns: 1fr;
      align-items: stretch;
    }

    .model-test-controls button {
      width: 100%;
    }

    .results-controls {
      flex-direction: column;
      gap: 10px;
    }

    .group-header {
      flex-direction: column;
      align-items: stretch;
    }

    .group-actions {
      width: 100%;
    }

    .compare-btn {
      width: 100%;
    }

    .result-model-row {
      flex-direction: column;
      align-items: flex-start;
    }

    .gaps-header {
      grid-template-columns: 60px 1fr 1fr;
      font-size: 10px;
      padding: 6px;
    }

    .gaps-row {
      grid-template-columns: 60px 1fr 1fr;
      padding: 6px;
      font-size: 10px;
    }

    .col-original,
    .col-filled {
      padding: 2px;
      font-size: 9px;
    }
  }
</style>
