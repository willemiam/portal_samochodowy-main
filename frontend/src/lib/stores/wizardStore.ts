import { writable } from 'svelte/store';

export interface PlatformConfig {
  // Basic Info
  name: string;
  description: string;
  domain: string;
  
  // Features
  features: string[];
  
  // Domain Details
  domainDetails: Record<string, any>;
  
  // Advanced
  advanced: {
    theme?: string;
    language?: string;
    [key: string]: any;
  };
}

const initialConfig: PlatformConfig = {
  name: '',
  description: '',
  domain: '',
  features: [],
  domainDetails: {},
  advanced: {}
};

export const wizardStore = writable<PlatformConfig>(initialConfig);

export function resetWizard() {
  wizardStore.set(initialConfig);
}
