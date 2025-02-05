export const API_URL = "http://127.0.0.1:5000"; 
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
  const response = await fetch(`${API_URL}/api/cars/makes`);
  return await response.json();
}

// Pobranie listy modeli dla danej marki
export async function fetchModels(make) {
  const response = await fetch(`${API_URL}/api/cars/models?make=${encodeURIComponent(make)}`);
  return await response.json();
}