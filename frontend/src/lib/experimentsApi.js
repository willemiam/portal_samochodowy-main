/**
 * Experiments API Client
 * Communicates with backend for A/B testing experiments
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";
const API_ENDPOINT = `${API_BASE_URL}/api`;

/**
 * Create a new experiment
 */
export async function createExperiment(experiment) {
  const response = await fetch(`${API_ENDPOINT}/experiments`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(experiment),
  });

  if (!response.ok) {
    throw new Error(`Failed to create experiment: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Get all experiments
 */
export async function getExperiments() {
  const response = await fetch(`${API_ENDPOINT}/experiments`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch experiments: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Get a specific experiment by ID
 */
export async function getExperiment(experimentId) {
  const response = await fetch(`${API_ENDPOINT}/experiments/${experimentId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch experiment: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Run an experiment on test items
 */
export async function runExperiment(experimentId, testItems) {
  const response = await fetch(
    `${API_ENDPOINT}/experiments/${experimentId}/run`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ items: testItems }),
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to run experiment: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Get experiment results
 */
export async function getExperimentResults(experimentId) {
  const response = await fetch(
    `${API_ENDPOINT}/experiments/${experimentId}/results`,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch results: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Export experiment results as CSV
 */
export async function exportResults(experimentId, format = "csv") {
  const response = await fetch(
    `${API_ENDPOINT}/experiments/${experimentId}/export?format=${format}`,
    {
      method: "GET",
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to export results: ${response.statusText}`);
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `experiment-${experimentId}-results.${format}`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

/**
 * Delete an experiment
 */
export async function deleteExperiment(experimentId) {
  const response = await fetch(`${API_ENDPOINT}/experiments/${experimentId}`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to delete experiment: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Get available models for comparison
 */
export async function getAvailableModels() {
  const response = await fetch(`${API_ENDPOINT}/models`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch models: ${response.statusText}`);
  }

  return await response.json();
}
