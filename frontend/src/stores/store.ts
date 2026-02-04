import { writable, derived } from "svelte/store";

export interface ExperimentConfig {
  id?: string;
  name: string;
  description?: string;
  models: string[];
  parameters: {
    temperature: number;
    max_tokens: number;
    gap_notation?: string;
  };
  created_at?: string;
  created_by?: string;
}

export interface GapResult {
  index: number;
  marker: string;
  choice: string;
  alternatives?: string[];
}

export interface ExperimentRunResult {
  id?: string;
  experiment_id?: string;
  item_id: string;
  model_name: string;
  original_text: string;
  filled_text: string;
  gaps: GapResult[];
  semantic_score?: number;
  domain_score?: number;
  grammar_score?: number;
  overall_score?: number;
  generation_time?: number;
}

export interface ExperimentResult {
  experiment_id: string;
  experiment_name: string;
  models_compared: string[];
  total_items: number;
  results: ExperimentRunResult[];
  created_at?: string;
}

// Store for currently selected experiment configuration
export const selectedExperiment = writable<ExperimentConfig | null>(null);

// Store for experiment results
export const experimentResults = writable<ExperimentResult | null>(null);

// Store for list of all experiments
export const experimentsList = writable<ExperimentConfig[]>([]);

// Store for loading state
export const isLoading = writable(false);

// Store for error messages
export const error = writable<string | null>(null);

// Derived store: are we currently viewing results?
export const isViewingResults = derived(
  experimentResults,
  $results => $results !== null
);
