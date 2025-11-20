import { API_URL } from '../api.js';

export interface PlatformResponse {
  id: string;
  config: any;
  created_at?: string;
}

export interface PreviewRequest {
  domain: string;
  item_data: Record<string, any>;
}

export interface PreviewResponse {
  enhanced_text: string;
  sources: any[];
  session_id: string;
}

export async function createPlatform(config: any): Promise<PlatformResponse> {
  try {
    const response = await fetch(`${API_URL}/api/platforms`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ config }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to create platform');
    }

    return await response.json();
  } catch (error) {
    console.error('Error creating platform:', error);
    throw error;
  }
}

export async function getPlatform(id: string): Promise<PlatformResponse> {
  try {
    const response = await fetch(`${API_URL}/api/platforms/${id}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to fetch platform');
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching platform:', error);
    throw error;
  }
}

export async function previewPlatform(
  id: string,
  previewData: PreviewRequest
): Promise<PreviewResponse> {
  try {
    const response = await fetch(`${API_URL}/api/platforms/${id}/preview`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(previewData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to generate preview');
    }

    return await response.json();
  } catch (error) {
    console.error('Error generating preview:', error);
    throw error;
  }
}
