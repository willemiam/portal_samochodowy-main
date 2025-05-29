<script>
    import PhotoGrid from "../components/PhotoGrid.svelte";
    import { filterItems, fetchMakes, fetchModels } from "../lib/api.js";
    let formPhotos = [];
    let make = "";
    let model = "";
    let year = "";
    let items = [];
    let makes = [];
    let models = [];
    let years = Array.from({ length: 30 }, (_, i) => 2024 - i); 
    let descriptionRef;

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

    export async function generateDescription(carData) {
        const response = await fetch(
            "http://localhost:8000/enhance-description",
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(carData),
            },
        );
        if (!response.ok) {
            throw new Error("Błąd generowania opisu");
        }
        const data = await response.json();
        return data.description;
    }

    async function handleGenerateDescription(event) {
        event.preventDefault();
        const carData = { make, model, year };
        try {
            const description = await generateDescription(carData);
            descriptionRef.value = description;
        } catch (e) {
            descriptionRef.value = "Błąd generowania opisu";
        }
    }
</script>

<div class="container">
    <div class="main-baner">
        <h3>Dodaj ogłoszenie swojego samochodu</h3>
        <p>
            Dodaj wszystkie wymagane parametry, a następnie skorzytaj z pomocy
            AI i wynegeruj opis samochodu jednym kliknięciem!
        </p>
    </div>
    <div class="search-box">
        <form class="search-form">            <div class="input-fields">
                <label class="form-label" for="advertisement-title">Tytuł Ogłoszenia*</label>
                <textarea name="" id="advertisement-title"></textarea>
            </div>
            <div class="input-fields">
                <label class="form-label" for="make-select">Marka*</label>
                <select id="make-select" bind:value={make} on:change={updateModels}>
                    <option value="">Wybierz</option>
                    {#each makes as brand}
                        <option value={brand}>{brand}</option>
                    {/each}
                </select>
            </div>
            <div class="input-fields">
                <label class="form-label" for="model-select">Model*</label>
                <select id="model-select" bind:value={model} disabled={!make}>
                    <option value="">Wybierz</option>
                    {#each models as m}
                        <option value={m}>{m}</option>
                    {/each}
                </select>
            </div>
            <div class="input-fields">
                <label class="form-label" for="year-select">Rok*</label>
                <select id="year-select" bind:value={year} type="number">
                    <option value="">Wybierz</option>
                    {#each years as y}
                        <option value={y}>{y}</option>
                    {/each}
                </select>
            </div>
            <div class="input-fields">
                <label class="form-label" for="advertisement-description">Opis Ogłoszenia*</label>
                <textarea
                    bind:this={descriptionRef}
                    id="advertisement-description"
                ></textarea>
            </div>
            <button class="auction-btn" on:click={handleGenerateDescription}
                >Generuj opis</button
            >
            <PhotoGrid />

            <button class="auction-btn" id="add-item-btn">Dodaj</button>
        </form>
    </div>
</div>

<style>
    .main-baner {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin: auto;
        max-width: 800px;

        padding: 0px;
        background:
            linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)),
            url("/images/hero-car.jpg") center/cover no-repeat;
        color: white;
        text-align: center;
    }    .main-baner h3 {
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
        gap: 0.8rem;
        column-gap: 0px;
    }
    .form-label {
        color: black;
    }
    #advertisement-title {
        margin: auto;
        display: flex;
        justify-content: center;
        align-items: center;
        min-width: 40rem;
        max-height: fit-content;
        font-size: 1rem;
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
    }
    #advertisement-description {
        min-width: 40rem;
        min-height: 8rem;
    }
    .auction-btn {
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
</style>
