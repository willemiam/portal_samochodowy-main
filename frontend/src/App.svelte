<script>
  import { Router, Link, Route } from "svelte-routing";

  import Navbar from "./components/Navbar.svelte";
  import Home from "./routes/home.svelte";
  import Experiments from "./routes/experiments.svelte";
  import ExperimentDetail from "./routes/experimentDetail.svelte";
  import Footer from "./components/Footer.svelte";

  export let url = "";
</script>

<Router {url}>
  <div class="app">
    <Navbar />
    <main>
      <Route path="/" component={Home} />
      <Route path="/experiments" component={Experiments} />
      <Route path="/experiments/:id" component={ExperimentDetail} />
    </main>

    <Footer />
  </div>
</Router>

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