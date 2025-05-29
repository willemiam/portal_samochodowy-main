<script>
    import { Link } from "svelte-routing";
</script>

<footer>
    <div class="container">
        <div class="footer-content">
            <div class="footer-section">
                <h3>BEST CARS</h3>
                <p>
                    Find your perfect car from our wide selection of new and
                    used vehicles.
                </p>
            </div>

            <div class="footer-section">
                <h3>Quick Links</h3>
                <ul class="footer-links">
                    <li><Link to="/">Home</Link></li>
                    <li><Link to="/filter">Search Cars</Link></li>
                    <li><Link to="/additem">Sell Your Car</Link></li>
                    <li><Link to="/about">About Us</Link></li>
                </ul>
            </div>

            <div class="footer-section">
                <h3>Contact</h3>
                <ul class="footer-links">
                    <li><Link to="/help">Help Center</Link></li>
                    <li><Link to="/contact">Contact Us</Link></li>
                    <li><Link to="/privacy">Privacy Policy</Link></li>
                    <li><Link to="/terms">Terms of Service</Link></li>
                </ul>
            </div>
        </div>

        <div class="copyright">
            &copy; {new Date().getFullYear()} BEST CARS. All rights reserved.
        </div>
    </div>
</footer>

<style>
    footer {
        background-color: var(--primary-color);
        color: white;
        padding: 2rem 0;
        margin-top: 2rem;
    }

    .footer-content {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 2rem;
    }

    .footer-section h3 {
        font-size: 1.2rem;
        margin-bottom: 1rem;
    }

    .footer-links {
        list-style: none;
    }

    .footer-links li {
        margin-bottom: 0.5rem;
    }

    .footer-links a {
        color: #ccc;
        text-decoration: none;
        transition: color 0.2s ease;
    }

    .footer-links a:hover {
        color: white;
    }

    .copyright {
        text-align: center;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        font-size: 0.9rem;
        color: #ccc;
    }
</style>