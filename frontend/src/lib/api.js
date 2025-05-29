export const API_URL = "http://localhost:5000"; 
// Jeśli backend działa na innym porcie, zmień na np. http://127.0.0.1:8000

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
  const response = await fetch(`${API_URL}/api/items`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(itemData),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to create item');
  }
  
  return await response.json();
}