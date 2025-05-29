<script>
    import { Link } from "svelte-routing";
    import { filterItems, fetchMakes, fetchModels } from "../lib/api.js";
    let make = "";
    let model = "";
    let year = "";
    let items = [];
    let makes = [];
    let models = [];
    let years = Array.from({ length: 30 }, (_, i) => 2024 - i);

    async function loadMakes() {
        makes = await fetchMakes();
    }
    loadMakes();

    async function updateModels() {
        if (make) {
            models = await fetchModels(make);
        } else {
            models = [];
        }
        model = "";
    }

    async function applyFilter() {
        items = await filterItems(make, model, year);
    }
</script>

<section class="main-baner">
    <div class="container">
        <h1>Find Your Perfect Car</h1>        <p>
            Browse thousands of new and used cars from trusted dealers and
            private sellers
        </p>
        
        <div class="action-buttons">
            <Link to="/addItem" class="sell-btn">Sell Your Car</Link>
        </div>
        <div class="search-box">
            <form class="search-form">
                <div class="input-fields">
                    <label class="form-label">Marka</label>
                    <select bind:value={make} on:change={updateModels}>
                        <option value="">Wybierz</option>
                        {#each makes as brand}
                            <option value={brand}>{brand}</option>
                        {/each}
                    </select>
                </div>
                <div class="input-fields">
                    <!-- Lista rozwijana dla modeli -->
                    <label class="form-label">Model</label>
                    <select bind:value={model} disabled={!make}>
                        <option value="">Wybierz</option>
                        {#each models as m}
                            <option value={m}>{m}</option>
                        {/each}
                    </select>
                </div>
                <div class="input-fields">
                    <label class="form-label">Rok</label>
                    <!-- <input
                        type="number"
                        bind:value={year}
                        placeholder="Od roku"
                    /> -->                    <select bind:value={year} type="number">
                        <option value="">Wybierz</option>
                        {#each years as y}
                            <option value={y}>{y}</option>
                        {/each}
                    </select>
                </div>

                <button id="search-btn" on:click={applyFilter}>Szukaj</button>
            </form>
        </div>
    </div>

    {#if items.length > 0}
        <ul>
            {#each items as item}
                <li>
                    <strong>{item.make} {item.model} ({item.year})</strong> - {item.price}
                    PLN
                </li>
            {/each}
        </ul>
    {:else}
        <p>Brak wyników filtrowania.</p>
    {/if}
</section>

<style>
    .main-baner {
        background:
            linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)),
            url("/images/hero-car.jpg") center/cover no-repeat;
        color: white;
        padding: 4rem 0;
        text-align: center;
    }

    .main-baner h1 {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }

    .main-baner p {
        font-size: 1.2rem;
        margin-bottom: 2rem;
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
    }

    .search-box {
        background-color: white;
        padding: 2rem;
        border-radius: 8px;
        max-width: 800px;
        margin: 0 auto;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .search-form {
        display: flex;
        justify-content: space-around;
        flex-wrap: wrap;
        gap: 1rem;
    }
    .form-label {
        color: black;
    }
    .input-fields {
        display: flex;
        flex-direction: column;
    }

    .search-form select {
        min-width: 11rem;
        max-width: 11rem;
        min-height: 3.25rem;
        max-height: 3.25rem;
        padding: 0.5rem;
        border: 1px solid var(--mid-gray);
        border-radius: 4px;
        font-size: 1rem;
    }

    .search-form button {
        padding: 0.75rem;
        font-size: 1rem;
    }    #search-btn {
        padding-left: 4rem;
        padding-right: 4rem;
        font-size: large;
        font-weight: bold;
        color: aliceblue;
        text-decoration: none;
        margin: auto;
        background-color: var(--accent-color);
        border-radius: 0.25rem;
        transition: all 0.2s ease;
    }

    .action-buttons {
        margin-top: 2rem;
        display: flex;
        justify-content: center;
        gap: 1rem;
    }

    .sell-btn {
        display: inline-block;
        padding: 1rem 2rem;
        background-color: #28a745;
        color: white;
        text-decoration: none;
        border-radius: 0.5rem;
        font-weight: bold;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .sell-btn:hover {
        background-color: #218838;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
</style>