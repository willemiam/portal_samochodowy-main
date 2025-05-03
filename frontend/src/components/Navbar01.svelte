<script>
    import { Link } from "svelte-routing";
</script>

<header class="header">
    <div>
        <h1 id="baner">Top Samochody</h1>
    </div>
    <nav class="menu">
        <ul>
            <li><Link to="/">Start</Link></li>
            <li><Link to="/Items">Ogłoszenia</Link></li>
            <li><Link to="/Filter">Filtruj Ogłoszenia</Link></li>
            <li><Link to="/">Kontakt</Link></li> <!-- Zrobic przekierowanie do danych kontakwoych na dole strony głównej-->
            <li><Link to="/Account">Konto</Link></li>
        </ul>
    </nav>
</header>

<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: 'Poppins', sans-serif;
        scroll-behavior: smooth;
        -webkit-scroll-behavior: smooth;
    }

    body {
        background-color: #fff;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .header {
        background-color: #ccc;
        height: 100px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 20px;
    }

    .header .menu {
        flex: 1;
        height: 100%;
    }

    /* ✅ Globalny styl dla listy */
    :global(.header .menu ul) {
        display: flex;
        list-style-type: none;
        align-items: center;
        justify-content: space-around;
        width: 100%;
        height: 100%;
    }

    /* ✅ Powiększamy `li` */
    :global(.header .menu ul li) {
        display: flex;
        align-items: center;
        justify-content: center;
        list-style: none;
        padding: 10px 20px; /* Powiększa obszar */
    }

    /* ✅ Powiększamy `a` (`Link`) */
    :global(.header .menu ul li a) {
        display: block; /* Sprawia, że a wypełnia cały li */
        width: 100%;  /* Wypełnia `li` */
        height: 100%; /* Wypełnia `li` */
        text-align: center;
        text-decoration: none;
        color: black;
        padding: 15px 20px; /* Zwiększa obszar */
        transition: 0.3s;
    }

    /* ✅ Powiększone podświetlenie */
    :global(.header .menu ul li a:hover) {
        background-color: #c00;
        color: #fff;
        border-radius: 5px;
    }
</style>
