<script>
    import { filterItems, fetchMakes, fetchModels } from "../lib/api.js";
    let make = "";
    let model = "";
    let year = "";
    let items = [];
    let makes = [];
    let models = [];
  
    // Pobierz listę marek przy załadowaniu komponentu
    async function loadMakes() {
      makes = await fetchMakes();
    }
    loadMakes();
  
    // Kiedy użytkownik wybierze markę, pobierz dostępne modele
    async function updateModels() {
      if (make) {
        models = await fetchModels(make);
      } else {
        models = [];
      }
      model = ""; // Resetujemy model po zmianie marki
    }
  
    async function applyFilter() {
      items = await filterItems(make, model, year);
    }
  </script>
  
  <h2>Filtruj Ogłoszenia</h2>
  
  <div>
    <!-- Lista rozwijana dla marek -->
    <select bind:value={make} on:change={updateModels}>
      <option value="">Wybierz markę</option>
      {#each makes as brand}
        <option value={brand}>{brand}</option>
      {/each}
    </select>
  
    <!-- Lista rozwijana dla modeli -->
    <select bind:value={model} disabled={!make}>
        <option value="">Wybierz model</option>
      {#each models as m}
        <option value={m}>{m}</option>
      {/each}
    </select>
  
    <input type="number" bind:value={year} placeholder="Rok" />
    <button on:click={applyFilter}>Szukaj</button>
  </div>
  
  {#if items.length > 0}
    <ul>
      {#each items as item}
        <li>
          <strong>{item.make} {item.model} ({item.year})</strong> - {item.price} PLN
        </li>
      {/each}
    </ul>
  {:else}
    <p>Brak wyników filtrowania.</p>
  {/if}
  