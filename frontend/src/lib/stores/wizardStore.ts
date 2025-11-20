import { writable } from 'svelte/store';

export interface PlatformConfig {
  name: string;
  description: string;
  domain: string;
  features: {
    search: boolean;
    filters: boolean;
    aiEnhancement: boolean;
    userAccounts: boolean;
  };
  domainDetails: {
    itemName: string;
    itemNamePlural: string;
    primaryFields: string[];
  };
  advanced: {
    mcpEndpoint: string;
    apiKey: string;
    customPrompt: string;
  };
}

export interface WizardState {
  currentStep: number;
  platformConfig: PlatformConfig;
  platformId: string | null;
  isSaving: boolean;
  error: string | null;
}

const initialState: WizardState = {
  currentStep: 0,
  platformConfig: {
    name: '',
    description: '',
    domain: '',
    features: {
      search: true,
      filters: true,
      aiEnhancement: false,
      userAccounts: false,
    },
    domainDetails: {
      itemName: '',
      itemNamePlural: '',
      primaryFields: [],
    },
    advanced: {
      mcpEndpoint: '',
      apiKey: '',
      customPrompt: '',
    },
  },
  platformId: null,
  isSaving: false,
  error: null,
};

function createWizardStore() {
  const { subscribe, set, update } = writable<WizardState>(initialState);

  return {
    subscribe,
    reset: () => set(initialState),
    setStep: (step: number) => update(state => ({ ...state, currentStep: step })),
    nextStep: () => update(state => ({ ...state, currentStep: state.currentStep + 1 })),
    prevStep: () => update(state => ({ ...state, currentStep: Math.max(0, state.currentStep - 1) })),
    updateConfig: (config: Partial<PlatformConfig>) => 
      update(state => ({
        ...state,
        platformConfig: { ...state.platformConfig, ...config }
      })),
    updateFeatures: (features: Partial<PlatformConfig['features']>) =>
      update(state => ({
        ...state,
        platformConfig: {
          ...state.platformConfig,
          features: { ...state.platformConfig.features, ...features }
        }
      })),
    updateDomainDetails: (details: Partial<PlatformConfig['domainDetails']>) =>
      update(state => ({
        ...state,
        platformConfig: {
          ...state.platformConfig,
          domainDetails: { ...state.platformConfig.domainDetails, ...details }
        }
      })),
    updateAdvanced: (advanced: Partial<PlatformConfig['advanced']>) =>
      update(state => ({
        ...state,
        platformConfig: {
          ...state.platformConfig,
          advanced: { ...state.platformConfig.advanced, ...advanced }
        }
      })),
    setSaving: (isSaving: boolean) => update(state => ({ ...state, isSaving })),
    setError: (error: string | null) => update(state => ({ ...state, error })),
    setPlatformId: (platformId: string | null) => update(state => ({ ...state, platformId })),
  };
}

export const wizardStore = createWizardStore();
