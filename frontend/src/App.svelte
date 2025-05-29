<script>
  import { Router, Link, Route } from "svelte-routing";
  import { onMount } from "svelte";
  import { wrap } from "svelte-spa-router/wrap";

  import auth from "./authService";
  import { isAuthenticated, user } from "./stores/store";

  import Navbar from "./components/Navbar.svelte";
  import Home from "./routes/home.svelte";
  import Account from "./routes/account.svelte";
  import AddItem from "./routes/addItem.svelte";
  import Filter from "./routes/filter.svelte";
  import Footer from "./components/Footer.svelte";

  export let url = "";
  onMount(async () => {
    await auth.checkAuth();
  });
</script>

<Router {url}>
  <div class="app">
    <Navbar />    <main>
      <Route path="/" component={Home} />
      <Route path="/addItem" component={AddItem} />
      <Route path="/account" component={Account} />
      <Route path="/filter" component={Filter} />
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