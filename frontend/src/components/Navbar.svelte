<script>
</script>

<header>
    <div class="container">
        <nav>
            <div class="logo">
                <!-- SVG Logo -->
                <svg
                    width="40"
                    height="30"
                    viewBox="0 0 40 30"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                >
                    <rect width="40" height="30" rx="4" fill="#1a3353" />
                    <path
                        d="M8 22C11.3137 22 14 19.3137 14 16C14 12.6863 11.3137 10 8 10C4.68629 10 2 12.6863 2 16C2 19.3137 4.68629 22 8 22Z"
                        fill="white"
                    />
                    <path
                        d="M32 22C35.3137 22 38 19.3137 38 16C38 12.6863 35.3137 10 32 10C28.6863 10 26 12.6863 26 16C26 19.3137 28.6863 22 32 22Z"
                        fill="white"
                    />
                    <path
                        d="M2 16H38M8 10L12 3H28L32 10M8 22H32"
                        stroke="white"
                        stroke-width="2"
                    />
                </svg>
                <span>A/B Testing</span>
            </div>
        </nav>
    </div>
</header>

<style>
    header {
        display: flex;
        justify-content: center;
        padding: 0px;
        margin: 0px;
        max-height: 5rem;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        position: sticky;
        top: 0;
        z-index: 100;
    }

    nav {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 1rem 0;
        margin: auto;
    }

    .logo {
        display: flex;
        align-items: center;
        color: var(--primary-color);
        font-weight: bold;
        font-size: 1.5rem;
        text-decoration: none;
    }

    .logo span {
        margin-left: 0.5rem;
    }
</style>