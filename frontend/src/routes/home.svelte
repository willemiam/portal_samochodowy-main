<script>
  import { onMount } from "svelte";
  import CarCard from "../components/CarCard.svelte";
  import CategoryFilter from "../components/CategoryFilter.svelte";
  import MainBanner from "../components/MainBanner.svelte";

  let featuredCars = [];

  onMount(async () => {

    try {
      const response = await fetch("/api/cars/featured");
      featuredCars = await response.json();
    } catch (error) {
      console.error("Error fetching featured cars:", error);
    }
  });
</script>

<svelte:head>
  <title>BEST CARS - Find Your Perfect Car</title>
</svelte:head>

<MainBanner />

<section class="section categories">
  <div class="container">
    <CategoryFilter />
  </div>
</section>

<section class="section featured-cars">
  <div class="container">
    <div class="section-title">
      <h2>Featured Cars</h2>
      <a href="/filter" class="view-all">View All</a>
    </div>

    <div class="grid">
      {#each featuredCars as car}
        <CarCard {car} />
      {:else}
        <p>Loading featured cars...</p>
      {/each}
    </div>
  </div>
</section>

<style>
  .categories {
    background-color: white;
  }

  .featured-cars {
    background-color: var(--light-gray);
  }

  .view-all {
    color: var(--accent-color);
    text-decoration: none;
    font-weight: 500;
  }
</style>