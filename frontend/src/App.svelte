<script>
  import { Router, Route } from "svelte-routing";
  import { onMount } from "svelte";
  import auth from "./authService";
  import { isAuthenticated, user } from "./stores/store";
  import Home from "./routes/Home.svelte";
  import Items from "./routes/items.svelte";
  import Filter from "./routes/filter.svelte";
  // import Kontakt from "./routes/Kontakt.svelte";
  import Navbar from "./components/Navbar01.svelte";
  import Account from "./routes/account.svelte"

  onMount(async () => {
    await auth.checkAuth();
  })
</script>

<Router>
  <Navbar />
  <Route path="/" component={Home} />
  <Route path="/Items" component={Items} />
  <Route path="/Filter" component={Filter}/>
  <Route path="/Account" component={Account}/>
  <!-- <Route path="/kontakt" component={Kontakt} /> -->
</Router>
