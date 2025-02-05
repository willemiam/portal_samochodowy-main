<script>
  import { fetchItems } from "../lib/api.js";
  let items = [];

  // Funkcja ładująca wszystkie ogłoszenia
  async function loadItems() {
    items = await fetchItems();
  }

  // Ładujemy ogłoszenia na starcie komponentu
  loadItems();
</script>

<h2>Lista Ogłoszeń</h2>

<!-- Wyświetlamy listę ogłoszeń -->
{#if items.length > 0}
  <ul>
    {#each items as item}
      <li>
        <strong>{item.make} {item.model} ({item.year})</strong> - {item.price} PLN
      </li>
    {/each}
  </ul>
{:else}
  <p>Brak ogłoszeń do wyświetlenia.</p>
{/if}
