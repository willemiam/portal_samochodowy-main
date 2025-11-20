<script>
    import CreatorWizard from "$lib/components/CreatorWizard.svelte";
    import "../app.css";
</script>

<svelte:head>
    <title>Platform Creator</title>
    <meta
        name="description"
        content="Create your own automotive platform with our wizard"
    />
</svelte:head>

<main class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <div class="container mx-auto px-4 py-8">
        <header class="text-center mb-8">
            <h1 class="text-4xl font-bold text-gray-900 mb-4">
                Platform Creator
            </h1>
            <p class="text-lg text-gray-600 max-w-2xl mx-auto">
                Create your own automotive marketplace platform with our
                easy-to-use wizard. Configure features, domains, and settings to
                build your perfect platform.
            </p>
        </header>

        <CreatorWizard />
    </div>
</main>

<style>
    :global(body) {
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
            sans-serif;
    }
</style>
