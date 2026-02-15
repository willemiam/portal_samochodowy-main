<script>
  import BulkGaps from "./routes/bulkGaps.svelte";
  import Navbar from "./components/Navbar.svelte";
</script>

<div class="app">
  <Navbar />
  <main>
    <BulkGaps />
  </main>
</div>

<style>
  .app {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  main {
    flex: 1;
  }
</style>