<script>
    import { onMount } from 'svelte';
    import PhotoGrid from "../components/PhotoGrid.svelte";
    import { fetchMakes, fetchModels, createItem } from "../lib/api.js";
    
    let formPhotos = [];
    let make = "";
    let model = "";
    let year = "";
    let price = "";
    let car_mileage = "";
    let color = "";
    let fuel_type = "";
    let engine_displacement = "";
    let car_size_class = "";
    let doors = "";
    let transmission = "";
    let drive_type = "";
    
    let makes = [];
    let models = [];
    let years = Array.from({ length: 30 }, (_, i) => 2024 - i); 
    let descriptionRef;
    
    let isSubmitting = false;
    let submitError = "";
    let submitSuccess = false;

    // Temporary user_id - in production this should come from auth
    const user_id = 1;    async function loadMakes() {
        try {
            console.log('Loading makes...');
            makes = await fetchMakes();
            console.log('Makes loaded successfully:', makes.length, 'items');
            if (makes.length === 0) {
                submitError = "No car makes could be loaded. Please check your connection.";
            }
        } catch (error) {
            console.error('Error loading makes:', error);
            submitError = `Error loading car makes: ${error.message}`;
            // Fallback to test data if API fails
            makes = ['BMW', 'Audi', 'Ford', 'Toyota', 'Mercedes-Benz'];
        }
    }
    
    onMount(() => {
        loadMakes();
    });

    async function updateModels() {
        if (make) {
            models = await fetchModels(make);
        } else {
            models = [];
        }
        model = "";
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

    async function handleSubmit(event) {
        event.preventDefault();
        
        // Reset previous states
        submitError = "";
        submitSuccess = false;
        
        // Validate required fields
        if (!make || !model || !year || !price || !car_mileage || !color || !descriptionRef?.value) {
            submitError = "Wypełnij wszystkie wymagane pola";
            return;
        }

        isSubmitting = true;

        try {
            const itemData = {
                user_id,
                make,
                model,
                year: parseInt(year),
                price: parseFloat(price),
                car_mileage: parseInt(car_mileage),
                color,
                description: descriptionRef.value,
                fuel_type: fuel_type || null,
                engine_displacement: engine_displacement ? parseFloat(engine_displacement) : null,
                car_size_class: car_size_class || null,
                doors: doors ? parseInt(doors) : null,
                transmission: transmission || null,
                drive_type: drive_type || null
            };

            await createItem(itemData);
            submitSuccess = true;
            
            // Reset form
            make = "";
            model = "";
            year = "";
            price = "";
            car_mileage = "";
            color = "";
            fuel_type = "";
            engine_displacement = "";
            car_size_class = "";
            doors = "";
            transmission = "";
            drive_type = "";
            descriptionRef.value = "";
            
        } catch (error) {
            submitError = error.message;
        } finally {
            isSubmitting = false;
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
    </div>    <div class="search-box">
        <form class="search-form" on:submit={handleSubmit}>
            
            {#if submitSuccess}
                <div class="success-message">
                    ✅ Ogłoszenie zostało pomyślnie dodane!
                </div>
            {/if}
            
            {#if submitError}
                <div class="error-message">
                    ❌ {submitError}
                </div>
            {/if}            <div class="input-fields">
                <label class="form-label" for="make-select">Marka*</label>
                <select id="make-select" bind:value={make} on:change={updateModels} required>
                    <option value="">Wybierz</option>
                    {#each makes as brand}
                        <option value={brand}>{brand}</option>
                    {/each}
                </select>
            </div>
            
            <div class="input-fields">
                <label class="form-label" for="model-select">Model*</label>
                <select id="model-select" bind:value={model} disabled={!make} required>
                    <option value="">Wybierz</option>
                    {#each models as m}
                        <option value={m}>{m}</option>
                    {/each}
                </select>
            </div>
            
            <div class="input-fields">
                <label class="form-label" for="year-select">Rok*</label>
                <select id="year-select" bind:value={year} required>
                    <option value="">Wybierz</option>
                    {#each years as y}
                        <option value={y}>{y}</option>
                    {/each}
                </select>
            </div>
            
            <div class="input-fields">
                <label class="form-label" for="price-input">Cena (PLN)*</label>
                <input id="price-input" type="number" bind:value={price} placeholder="np. 45000" required />
            </div>
            
            <div class="input-fields">
                <label class="form-label" for="mileage-input">Przebieg (km)*</label>
                <input id="mileage-input" type="number" bind:value={car_mileage} placeholder="np. 120000" required />
            </div>
            
            <div class="input-fields">
                <label class="form-label" for="color-input">Kolor*</label>
                <input id="color-input" type="text" bind:value={color} placeholder="np. Czerwony" required />
            </div>
            
            <div class="input-fields">
                <label class="form-label" for="fuel-type-select">Rodzaj paliwa</label>
                <select id="fuel-type-select" bind:value={fuel_type}>
                    <option value="">Wybierz</option>
                    <option value="Benzyna">Benzyna</option>
                    <option value="Diesel">Diesel</option>
                    <option value="Hybryda">Hybryda</option>
                    <option value="Elektryczny">Elektryczny</option>
                    <option value="LPG">LPG</option>
                </select>
            </div>
            
            <div class="input-fields">
                <label class="form-label" for="engine-input">Pojemność silnika (L)</label>
                <input id="engine-input" type="number" step="0.1" bind:value={engine_displacement} placeholder="np. 2.0" />
            </div>
            
            <div class="input-fields">
                <label class="form-label" for="car-class-select">Klasa pojazdu</label>
                <select id="car-class-select" bind:value={car_size_class}>
                    <option value="">Wybierz</option>
                    <option value="Compact">Compact</option>
                    <option value="Sedan">Sedan</option>
                    <option value="SUV">SUV</option>
                    <option value="Hatchback">Hatchback</option>
                    <option value="Coupe">Coupe</option>
                    <option value="Station Wagon">Station Wagon</option>
                </select>
            </div>
            
            <div class="input-fields">
                <label class="form-label" for="doors-select">Liczba drzwi</label>
                <select id="doors-select" bind:value={doors}>
                    <option value="">Wybierz</option>
                    <option value="2">2</option>
                    <option value="3">3</option>
                    <option value="4">4</option>
                    <option value="5">5</option>
                </select>
            </div>
            
            <div class="input-fields">
                <label class="form-label" for="transmission-select">Skrzynia biegów</label>
                <select id="transmission-select" bind:value={transmission}>
                    <option value="">Wybierz</option>
                    <option value="Manual">Manualna</option>
                    <option value="Automatic">Automatyczna</option>
                    <option value="CVT">CVT</option>
                </select>
            </div>
            
            <div class="input-fields">
                <label class="form-label" for="drive-type-select">Napęd</label>
                <select id="drive-type-select" bind:value={drive_type}>
                    <option value="">Wybierz</option>
                    <option value="FWD">Przedni (FWD)</option>
                    <option value="RWD">Tylny (RWD)</option>
                    <option value="AWD">Wszystkie koła (AWD)</option>
                    <option value="4WD">4x4 (4WD)</option>
                </select>
            </div>
            
            <div class="input-fields">
                <label class="form-label" for="advertisement-description">Opis Ogłoszenia*</label>
                <textarea
                    bind:this={descriptionRef}
                    id="advertisement-description"
                    placeholder="Opisz swój samochód..."
                    required
                ></textarea>
            </div>
            
            <button type="button" class="auction-btn" on:click={handleGenerateDescription}>
                Generuj opis AI
            </button>
            
            <PhotoGrid />

            <button type="submit" class="auction-btn" id="add-item-btn" disabled={isSubmitting}>
                {isSubmitting ? 'Dodawanie...' : 'Dodaj ogłoszenie'}
            </button>
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
    }    .form-label {
        color: black;
    }
    
    .input-fields {
        display: flex;
        flex-direction: column;
    }.search-form select {
        min-width: 11rem;
        max-width: 11rem;
        min-height: 3.25rem;
        max-height: 3.25rem;
        padding: 0.5rem;
        border: 1px solid var(--mid-gray);
        border-radius: 4px;
        font-size: 1rem;
    }

    .search-form input {
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
    
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 4px;
        border: 1px solid #c3e6cb;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 4px;
        border: 1px solid #f5c6cb;
        margin-bottom: 1rem;
        text-align: center;
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
