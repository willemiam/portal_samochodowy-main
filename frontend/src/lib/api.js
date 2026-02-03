export const API_URL = "http://localhost:5000"; 
// Jeśli backend działa na innym porcie, zmień na np. http://127.0.0.1:8000

import auth from '../authService.ts';

// Helper function to get authorization headers
async function getAuthHeaders() {
    const token = await auth.getAccessToken();
    const headers = {
        'Content-Type': 'application/json',
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
}

// Pobranie wszystkich ogłoszeń
export async function fetchItems() {
  const response = await fetch(`${API_URL}/api/items`);
  return await response.json();
}

// Filtrowanie ogłoszeń
export async function filterItems(make, model, year) {
  const url = new URL(`${API_URL}/api/items/filter`);
  if (make) url.searchParams.append('make', make);
  if (model) url.searchParams.append('model', model);
  if (year) url.searchParams.append('year', year);

  const response = await fetch(url);
  return await response.json();
}

// Pobranie listy unikalnych marek
export async function fetchMakes() {
  try {
    const response = await fetch(`${API_URL}/api/cars/makes`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const makes = await response.json();
    console.log('API response for makes:', makes);
    return makes;
  } catch (error) {
    console.error('Error fetching makes:', error);
    throw error;
  }
}

// Pobranie listy modeli dla danej marki
export async function fetchModels(make) {
  const response = await fetch(`${API_URL}/api/cars/models?make=${encodeURIComponent(make)}`);
  return await response.json();
}

// Tworzenie nowego ogłoszenia
export async function createItem(itemData) {
  const headers = await getAuthHeaders();
  
  // Remove user_id from itemData since it comes from auth token
  const { user_id, ...cleanItemData } = itemData;
  
  const response = await fetch(`${API_URL}/api/items`, {
    method: 'POST',
    headers,
    body: JSON.stringify(cleanItemData),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to create item');
  }
  
  return await response.json();
}

// ============ MCP SERVICE FUNCTIONS ============

/**
 * Construct text with gap markers from car form data
 */
export function constructTextWithGaps(carData) {
  const { make, model, year, mileage, condition, fuel_type } = carData;
  
  // Template pattern: Year Make [GAP:1] with [GAP:2] engine, mileage
  const text_with_gaps = `${year} ${make} [GAP:1] z [GAP:2] silnikiem, ${mileage} km`;
  
  return {
    text_with_gaps,
    attributes: {
      year,
      make,
      model,
      condition,
      fuel_type
    }
  };
}

/**
 * Build MCP request from car form data
 */
export function buildMCPRequest(carData, itemId = null) {
  const { text_with_gaps, attributes } = constructTextWithGaps(carData);
  
  return {
    domain: "cars",
    model: "bielik-1.5b-gguf",
    items: [
      {
        id: itemId || `ad-${Date.now()}`,
        text_with_gaps,
        attributes
      }
    ],
    options: {
      language: "pl",
      temperature: 0.3,
      max_new_tokens: 200,
      top_n_per_gap: 1
    }
  };
}

/**
 * Call MCP service for gap-filling
 */
export async function callMCPService(request) {
  const MCP_URL = import.meta.env.VITE_MCP_SERVICE_URL || "http://localhost:8001";
  
  const response = await fetch(
    `${MCP_URL}/api/v1/enhance-description`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request)
    }
  );
  
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`MCP Error ${response.status}: ${error}`);
  }
  
  const data = await response.json();
  
  // Extract filled text from response
  if (data.items && data.items[0]) {
    const item = data.items[0];
    if (item.status === "ok" || item.status === "warning") {
      return {
        filled_text: item.filled_text,
        gaps: item.gaps,
        status: item.status
      };
    } else {
      throw new Error(item.error || "Gap filling failed");
    }
  }
  
  throw new Error("Invalid MCP response structure");
}