<script>
    export let car;
</script>

<div class="car-card">
    <div
        class="car-image"
        style="background-image: url({car.imageUrl ||
            '/images/car-placeholder.jpg'})"
    ></div>
    <div class="car-details">
        <div class="car-title">{car.make} {car.model} {car.variant}</div>
        <div class="car-info">
            {car.year} | {car.mileage}km | {car.fuelType} | {car.horsePower}KM
        </div>
        <div class="car-price">{car.price.toLocaleString()} PLN</div>
        <div class="car-tags">
            <span class="car-tag">{car.bodyType}</span>
            <span class="car-tag">{car.transmission}</span>
            {#if car.isSpecialOffer}
                <span class="car-tag special">Special Offer</span>
            {/if}
        </div>
    </div>
</div>

<style>
    .car-card {
        background-color: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition:
            transform 0.2s ease,
            box-shadow 0.2s ease;
    }

    .car-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }

    .car-image {
        height: 200px;
        background-position: center;
        background-size: cover;
        background-repeat: no-repeat;
    }

    .car-details {
        padding: 1rem;
    }

    .car-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
    }

    .car-info {
        color: var(--dark-gray);
        margin-bottom: 1rem;
        font-size: 0.9rem;
    }

    .car-price {
        font-weight: 600;
        font-size: 1.25rem;
        color: var(--accent-color);
    }

    .car-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }

    .car-tag {
        background-color: var(--light-gray);
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        color: var(--dark-gray);
    }

    .car-tag.special {
        background-color: #ffe8cc;
        color: #e67700;
    }
</style>