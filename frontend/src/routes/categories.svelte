<script>
    import { onMount } from 'svelte';
    import { link } from 'svelte-routing';
    import { fetchCategories } from '../lib/api.js';

    let categories = [];
    let error = null;

    onMount(async () => {
        try {
            categories = await fetchCategories();
        } catch (e) {
            error = e.message;
        }
    });
</script>

<div class="container">
    <h1>Select a Category</h1>
    {#if error}
        <p class="error">{error}</p>
    {/if}
    <ul>
        {#each categories as category}
            <li>
                <a href={`/add-item/${category.id}`} use:link>{category.name}</a>
            </li>
        {/each}
    </ul>
</div>
