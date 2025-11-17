<script>
    import { onMount } from 'svelte';
    import { useParams } from 'svelte-routing';
    import PhotoGrid from "../components/PhotoGrid.svelte";
    import { fetchCategorySchema, createItem } from "../lib/api.js";
    import { isAuthenticated, user } from "../stores/store.ts";
    import auth from "../authService.ts";

    const { category_id } = useParams();

    let formPhotos = [];
    let photoGridRef;
    let price = "";
    let descriptionRef;
    let isSubmitting = false;
    let isGeneratingDescription = false;
    let submitError = "";
    let submitSuccess = false;
    let isAuthenticatedValue = false;
    let userValue = null;

    let category;
    let schema = [];
    let attributes = {};

    isAuthenticated.subscribe(value => {
        isAuthenticatedValue = value;
    });
    user.subscribe(value => {
        userValue = value;
    });

    onMount(async () => {
        try {
            const schemaData = await fetchCategorySchema(category_id);
            category = schemaData.category;
            schema = schemaData.schema;
        } catch (error) {
            submitError = `Error loading category schema: ${error.message}`;
        }
    });

    export async function generateDescription(domain, data) {
        const userToken = await auth.getAccessToken();
        if (!userToken) {
            throw new Error('Musisz być zalogowany, aby użyć generatora opisu AI');
        }
        
        const AI_SERVICE_URL = import.meta.env.VITE_AI_SERVICE_URL || "http://localhost:8080";
        
        const response = await fetch(
            `${AI_SERVICE_URL}/api/v1/enhance-description`,
            {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${userToken}`
                },
                body: JSON.stringify({
                    domain: domain,
                    data: data,
                    mcp_rules: {}
                }),
            },
        );
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Błąd serwera AI (${response.status}): ${errorText}`);
        }
        
        const responseData = await response.json();
        return responseData.description;
    }

    async function handleGenerateDescription(event) {
        event.preventDefault();
        
        if (!isAuthenticatedValue) {
            submitError = "Musisz być zalogowany, aby korzystać z generatora opisu AI";
            return;
        }
        
        try {
            isGeneratingDescription = true;
            const description = await generateDescription(category.slug, attributes);
            if (descriptionRef) {
                descriptionRef.value = description;
            }
            submitError = ""; 
        } catch (e) {
            submitError = `Błąd generowania opisu AI: ${e.message}`;
        } finally {
            isGeneratingDescription = false;
        }
    }

    async function handleSubmit(event) {
        event.preventDefault();
        submitError = "";
        submitSuccess = false;
        if (!isAuthenticatedValue) {
            submitError = "Musisz być zalogowany, aby dodać ogłoszenie";
            return;
        }
        
        if (!price || !descriptionRef?.value) {
            submitError = "Wypełnij wszystkie wymagane pola";
            return;
        }

        isSubmitting = true;

        try {
            const itemData = {
                category_id: category.id,
                price: parseFloat(price),
                description: descriptionRef.value,
                attributes: attributes
            };

            const createdItem = await createItem(itemData);
            
            if (photoGridRef && createdItem && createdItem.id) {
                const photosData = photoGridRef.getPhotosData();
                
                if (photosData.length > 0) {
                    const response = await fetch(`/api/items/${createdItem.id}/photos`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                        },
                        body: JSON.stringify({ photos: photosData })
                    });

                    if (!response.ok) {
                        const errorData = await response.json();
                        console.warn('Photo upload failed:', errorData.error);
                    }
                }
            }
            submitSuccess = true;
            
            price = "";
            if (descriptionRef) {
                descriptionRef.value = "";
            }
            attributes = {};
            
        } catch (error) {
            submitError = error.message;
        } finally {
            isSubmitting = false;
        }
    }
</script>

<div class="container">
    {#if category}
    <div class="main-baner">
        <h3>Dodaj ogłoszenie w kategorii: {category.name}</h3>
        <p>
            Dodaj wszystkie wymagane parametry, a następnie skorzystaj z pomocy
            AI i wygeneruj opis jednym kliknięciem!
        </p>
    </div>
    {/if}

    <div class="search-box">
        {#if !isAuthenticatedValue}
            <div class="auth-required-message">
                <h4>🔐 Logowanie wymagane</h4>
                <p>Aby dodać ogłoszenie, musisz być zalogowany.</p>
                <button type="button" class="auction-btn" on:click={() => auth.loginWithPopup()}>
                    Zaloguj się
                </button>
            </div>
        {:else}
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
            {/if}

            {#each schema as field}
                <div class="input-fields">
                    <label class="form-label" for={field.fieldName}>{field.fieldLabel}{#if field.isRequired}*{/if}</label>
                    {#if field.fieldType === 'text'}
                        <input id={field.fieldName} type="text" bind:value={attributes[field.fieldName]} required={field.isRequired} />
                    {:else if field.fieldType === 'number'}
                        <input id={field.fieldName} type="number" bind:value={attributes[field.fieldName]} required={field.isRequired} />
                    {:else if field.fieldType === 'select'}
                        <select id={field.fieldName} bind:value={attributes[field.fieldName]} required={field.isRequired}>
                            <option value="">Wybierz</option>
                            {#each field.fieldOptions as option}
                                <option value={option}>{option}</option>
                            {/each}
                        </select>
                    {/if}
                </div>
            {/each}
            
            <div class="input-fields">
                <label class="form-label" for="price-input">Cena (PLN)*</label>
                <input id="price-input" type="number" bind:value={price} placeholder="np. 45000" required />
            </div>

            <div class="input-fields">
                <label class="form-label" for="advertisement-description">Opis Ogłoszenia*</label>
                <textarea
                    bind:this={descriptionRef}
                    id="advertisement-description"
                    placeholder="Opisz swój przedmiot..."
                    required
                ></textarea>
            </div>
            
            <div class="ai-generation-section">
                <p class="ai-hint">💡 Wypełnij powyższe pola, aby wygenerować opis przy pomocy AI</p>
                <button type="button" class="auction-btn" on:click={handleGenerateDescription} disabled={isGeneratingDescription || !isAuthenticatedValue}>
                    {isGeneratingDescription ? 'Generuję opis...' : !isAuthenticatedValue ? 'Zaloguj się, aby użyć AI' : 'Generuj opis AI'}
                </button>
                {#if !isAuthenticatedValue}
                    <p class="auth-hint">🔐 Musisz być zalogowany, aby korzystać z generatora opisu AI</p>
                {/if}
            </div>
            
            <PhotoGrid bind:this={photoGridRef} />

            <button type="submit" class="auction-btn" id="add-item-btn" disabled={isSubmitting}>
                {isSubmitting ? 'Dodawanie...' : 'Dodaj ogłoszenie'}
            </button>
        </form>
        {/if}
    </div>
</div>

<style>
    /* Styles remain the same */
</style>
