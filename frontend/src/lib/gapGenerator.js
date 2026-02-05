/**
 * Gap Generator - Creates [GAP:n] markers by removing random words only
 * Numbers, punctuation, and special characters are preserved
 * 
 * Example:
 * Input: "BMW 320i zadbane 2020 45000km piękny silnik benzynowy"
 * Output: "BMW 320i [GAP:1] 2020 45000km [GAP:2] silnik [GAP:3]"
 */

/**
 * Get available models from Bielik service
 */
export async function getAvailableModels() {
  // Use localhost for local development, fallback to HF Space
  const BIELIK_URL = import.meta.env.VITE_AI_SERVICE_URL || "http://localhost:8000";
  
  try {
    const response = await fetch(`${BIELIK_URL}/models`);
    if (!response.ok) {
      console.warn(`Bielik /models returned ${response.status}, using fallback`);
      throw new Error(`Failed to fetch models: ${response.status}`);
    }
    
    const data = await response.json();
    console.log("Raw models from Bielik:", data);
    
    // Bielik returns {"models": [...]} wrapper
    let modelsList = Array.isArray(data) ? data : (data.models || []);
    
    if (!Array.isArray(modelsList) || modelsList.length === 0) {
      console.warn("Models response is not valid array, using fallback");
      throw new Error("Invalid models response format");
    }
    
    // Map all models, providing defaults for missing fields
    const mappedModels = modelsList.map(m => ({
      name: m.name || "unknown",
      type: m.type || "unknown",
      size: m.size || "unknown",
      polish_support: m.polish_support || "unknown",
      model_id: m.model_id || m.id || "unknown",
      loaded: m.loaded || false,
      active: m.active || false
    }));
    
    console.log("Mapped models:", mappedModels);
    return mappedModels;
  } catch (error) {
    console.error("Error fetching models from Bielik:", error);
    console.log("Using fallback models");
    
    // Fallback to default models - always works
    return [
      { name: "bielik-1.5b-transformer", type: "transformer", size: "2.4GB", polish_support: "excellent", loaded: false, active: false },
      { name: "bielik-11b-transformer", type: "transformer", size: "22GB", polish_support: "excellent", loaded: false, active: false },
      { name: "llama-3.1-8b", type: "inference_api", size: "8B", polish_support: "excellent", loaded: false, active: false }
    ];
  }
}

/**
 * Check if token contains letters (is a word, not just numbers)
 */
function isWord(token) {
  // Match any letter: Latin, Polish characters, etc.
  return /[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]/.test(token);
}

/**
 * Remove only WORDS from text and replace with [GAP:n] markers
 * Preserves all numbers, punctuation, and structure
 * 
 * @param {string} text - Input text
 * @param {number} removalPercent - Percentage of words to remove (0-100)
 * @returns {object} {text_with_gaps, word_count, gaps_created}
 */
export function createGapsInText(text, removalPercent = 10) {
  if (!text || text.trim().length === 0) {
    throw new Error("Text cannot be empty");
  }

  if (removalPercent < 0 || removalPercent > 100) {
    throw new Error("Removal percent must be 0-100");
  }

  // Split on whitespace, preserve structure
  const tokens = text.split(/\s+/);

  // Find all word token indices (not pure numbers)
  const wordIndices = [];
  tokens.forEach((token, idx) => {
    if (isWord(token)) {
      wordIndices.push(idx);
    }
  });

  if (wordIndices.length === 0) {
    throw new Error("No words found to remove (only numbers?)");
  }

  // Calculate how many words to remove
  const numToRemove = Math.ceil(wordIndices.length * (removalPercent / 100));

  // Randomly select word indices to remove
  const indicesToRemove = new Set();
  while (indicesToRemove.size < numToRemove) {
    const randomWordIdx = wordIndices[Math.floor(Math.random() * wordIndices.length)];
    indicesToRemove.add(randomWordIdx);
  }

  // Replace selected words with [GAP:n]
  let gapIndex = 1;
  const result = tokens.map((token, idx) => {
    if (indicesToRemove.has(idx)) {
      return `[GAP:${gapIndex++}]`;
    }
    return token;
  }).join(' ');

  return {
    text_with_gaps: result,
    word_count: wordIndices.length,
    gaps_created: numToRemove,
    removal_percent: removalPercent
  };
}

/**
 * Build MCP request for gap-filling
 * @param {string} text_with_gaps - Text with [GAP:n] markers
 * @param {string} model - Model name (default: bielik-1.5b-gguf)
 * @returns {object} MCP request object
 */
export function buildMCPRequest(text_with_gaps, model = "bielik-1.5b-gguf") {
  return {
    domain: "cars",
    model: model,
    items: [
      {
        id: `bulk-${Date.now()}`,
        text_with_gaps: text_with_gaps,
        attributes: {
          bulk: true,
          source: "bulk-gaps-feature"
        }
      }
    ],
    options: {
      language: "pl",
      temperature: 0.3,
      max_new_tokens: 300,
      top_n_per_gap: 1
    }
  };
}

/**
 * Call MCP service for gap-filling
 * @param {object} request - MCP request object
 * @returns {object} {filled_text, gaps, status, processing_time_ms}
 */
export async function callMCPService(request) {
  const MCP_URL = import.meta.env.VITE_MCP_SERVICE_URL || "http://localhost:8001";

  const startTime = performance.now();
  const response = await fetch(`${MCP_URL}/api/v1/enhance-description`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request)
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`MCP Error ${response.status}: ${error}`);
  }

  const data = await response.json();
  const endTime = performance.now();
  const processing_time_ms = Math.round(endTime - startTime);

  // Extract filled text from response
  if (data.items && data.items[0]) {
    const item = data.items[0];
    if (item.status === "ok" || item.status === "warning") {
      return {
        filled_text: item.filled_text,
        gaps: item.gaps || [],
        status: item.status,
        processing_time_ms: processing_time_ms,
        model: data.model,
        item_id: item.id
      };
    } else {
      throw new Error(item.error || "Gap filling failed");
    }
  }

  throw new Error("Invalid MCP response structure");
}

/**
 * Save result to local storage
 * @param {object} result - Result to save
 */
export function saveResult(result) {
  const results = JSON.parse(localStorage.getItem("bulkGapsResults") || "[]");
  
  const entry = {
    id: `result-${Date.now()}`,
    timestamp: new Date().toISOString(),
    ...result
  };
  
  results.push(entry);
  localStorage.setItem("bulkGapsResults", JSON.stringify(results));
  
  return entry.id;
}

/**
 * Get all saved results
 * @returns {array} All saved results
 */
export function getSavedResults() {
  return JSON.parse(localStorage.getItem("bulkGapsResults") || "[]");
}

/**
 * Get results by model
 * @param {string} model - Model name
 * @returns {array} Results for that model
 */
export function getResultsByModel(model) {
  const all = getSavedResults();
  return all.filter(r => r.model === model);
}

/**
 * Delete result
 * @param {string} resultId - Result ID to delete
 */
export function deleteResult(resultId) {
  const results = JSON.parse(localStorage.getItem("bulkGapsResults") || "[]");
  const filtered = results.filter(r => r.id !== resultId);
  localStorage.setItem("bulkGapsResults", JSON.stringify(filtered));
}

/**
 * Load bulk ads from retrieval service
 * @param {number} count - Number of ads to retrieve (default: 50)
 * @param {boolean} wordsOnly - Exclude numbers from text (default: true)
 * @returns {string} Concatenated bulk text from random ads
 */
export async function loadBulkAds(count = 50, wordsOnly = true) {
  const RETRIEVAL_URL = import.meta.env.VITE_RETRIEVAL_SERVICE_URL || "http://localhost:8003";
  
  try {
    const params = new URLSearchParams({
      count: count,
      words_only: wordsOnly
    });
    
    const response = await fetch(`${RETRIEVAL_URL}/retrieve?${params}`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || `Retrieval service error: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.status !== "success") {
      throw new Error("Failed to retrieve ads");
    }
    
    return {
      bulk_text: data.bulk_text,
      count: data.count,
      seed: data.seed
    };
  } catch (error) {
    console.error("Error loading bulk ads:", error);
    throw new Error(`Failed to load ads: ${error.message}`);
  }
}
