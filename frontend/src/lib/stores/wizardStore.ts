/**
 * Wizard Store - Manages state for the multi-step Platform Creator wizard
 */
import { writable } from 'svelte/store';

export interface PlatformData {
  // Basic Info
  name: string;
  description: string;
  domain: string;
  
  // Features
  features: string[];
  
  // Domain Details
  targetAudience: string;
  primaryGoals: string[];
  
  // Advanced
  customSettings: Record<string, any>;
  
  // Metadata
  id?: string;
  created_at?: string;
}

export interface WizardState {
  currentStep: number;
  platformData: PlatformData;
  totalSteps: number;
  isLoading: boolean;
  error: string | null;
}

const initialState: WizardState = {
  currentStep: 0,
  totalSteps: 5,
  platformData: {
    name: '',
    description: '',
    domain: '',
    features: [],
    targetAudience: '',
    primaryGoals: [],
    customSettings: {}
  },
  isLoading: false,
  error: null
};

function createWizardStore() {
  const { subscribe, set, update } = writable<WizardState>(initialState);

  return {
    subscribe,
    
    nextStep: () => update(state => ({
      ...state,
      currentStep: Math.min(state.currentStep + 1, state.totalSteps - 1)
    })),
    
    prevStep: () => update(state => ({
      ...state,
      currentStep: Math.max(state.currentStep - 1, 0)
    })),
    
    goToStep: (step: number) => update(state => ({
      ...state,
      currentStep: Math.max(0, Math.min(step, state.totalSteps - 1))
    })),
    
    updatePlatformData: (data: Partial<PlatformData>) => update(state => ({
      ...state,
      platformData: { ...state.platformData, ...data }
    })),
    
    setLoading: (isLoading: boolean) => update(state => ({
      ...state,
      isLoading
    })),
    
    setError: (error: string | null) => update(state => ({
      ...state,
      error
    })),
    
    reset: () => set(initialState)
  };
}

export const wizardStore = createWizardStore();
