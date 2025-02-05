<script>
  import { Router, Route } from "svelte-routing";
  import Home from "./routes/Home.svelte";
  import Items from "./routes/items.svelte";
  import Filter from "./routes/filter.svelte";
  // import Kontakt from "./routes/Kontakt.svelte";
  import Navbar from "./components/Navbar01.svelte";
  import Account from "./routes/account.svelte"
</script>

<Router>
  <Navbar />
  <Route path="/" component={Home} />
  <Route path="/Items" component={Items} />
  <Route path="/Filter" component={Filter}/>
  <Route path="/Account" component={Account}/>
  <!-- <Route path="/kontakt" component={Kontakt} /> -->
</Router>
