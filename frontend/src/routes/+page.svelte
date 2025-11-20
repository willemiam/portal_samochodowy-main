<script lang="ts">
  import CreatorWizard from '../lib/components/CreatorWizard.svelte';
</script>

<div class="page-container">
  <CreatorWizard />
</div>

<style>
  .page-container {
    min-height: 100vh;
    background: linear-gradient(to bottom, #f5f5f5, #e8e8e8);
    padding: 2rem 1rem;
  }

  :global(body) {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
      'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
      sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
</style>
