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
export async function filterItems(filters) {
  const url = new URL(`${API_URL}/api/items/filter`);
  for (const key in filters) {
    if (filters[key]) {
      url.searchParams.append(key, filters[key]);
    }
  }

  const response = await fetch(url);
  return await response.json();
}

// Pobranie wszystkich kategorii
export async function fetchCategories() {
  try {
    const response = await fetch(`${API_URL}/api/categories`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const categories = await response.json();
    console.log('API response for categories:', categories);
    return categories;
  } catch (error) {
    console.error('Error fetching categories:', error);
    throw error;
  }
}

// Pobranie schematu kategorii
export async function fetchCategorySchema(categoryId) {
  try {
    const response = await fetch(`${API_URL}/api/categories/${categoryId}/schema`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const schema = await response.json();
    console.log('API response for schema:', schema);
    return schema;
  } catch (error) {
    console.error('Error fetching schema:', error);
    throw error;
  }
}

// Tworzenie nowego ogłoszenia
export async function createItem(itemData) {
  const headers = await getAuthHeaders();
  
  const response = await fetch(`${API_URL}/api/items`, {
    method: 'POST',
    headers,
    body: JSON.stringify(itemData),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to create item');
  }
  
  return await response.json();
}