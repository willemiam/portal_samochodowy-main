const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

export interface CreatePlatformResponse {
  id: string;
  message: string;
  platform_config: any;
}

export interface PreviewResponse {
  id: string;
  enhanced_text: string;
  sources: string[];
  session_id: string;
  created_at: string;
}

export interface PreviewRequest {
  domain: string;
  item_data: Record<string, any>;
}

export async function createPlatform(platformConfig: any): Promise<CreatePlatformResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/platforms`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ platform_config: platformConfig }),
    });

    if (!response.ok) {
      throw new Error(`Failed to create platform: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error creating platform:', error);
    throw error;
  }
}

export async function getPlatform(platformId: string): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/platforms/${platformId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to get platform: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error getting platform:', error);
    throw error;
  }
}

export async function previewPlatform(
  platformId: string,
  previewRequest: PreviewRequest
): Promise<PreviewResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/platforms/${platformId}/preview`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(previewRequest),
    });

    if (!response.ok) {
      throw new Error(`Failed to preview platform: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error previewing platform:', error);
    throw error;
  }
}
