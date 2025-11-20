/**
 * Platform API - Functions to interact with the platform endpoints
 */

const API_URL = "http://localhost:5000";

export interface PlatformResponse {
  id: string;
  created_at: string;
}

export interface PreviewResponse {
  id: string;
  platform_id: string;
  enhanced_text: string;
  sources: any[];
  session_id: string;
  created_at: string;
}

/**
 * Create a new platform
 * @param platformData - The platform configuration data
 * @returns Promise with platform ID and created_at timestamp
 */
export async function createPlatform(platformData: any): Promise<PlatformResponse> {
  try {
    const response = await fetch(`${API_URL}/api/platforms`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(platformData),
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

/**
 * Get a platform by ID
 * @param platformId - The platform ID
 * @returns Promise with platform data
 */
export async function getPlatform(platformId: string): Promise<any> {
  try {
    const response = await fetch(`${API_URL}/api/platforms/${platformId}`);
    
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

/**
 * Generate a preview for a platform
 * @param platformId - The platform ID
 * @returns Promise with preview data including enhanced text
 */
export async function createPreview(platformId: string): Promise<PreviewResponse> {
  try {
    const response = await fetch(`${API_URL}/api/platforms/${platformId}/preview`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
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
