<script>
    import { navigate } from "svelte-routing";

    const categories = [
        { id: "sedan", name: "Sedan", icon: "sedan-icon" },
        { id: "suv", name: "SUV", icon: "suv-icon" },
        { id: "hatchback", name: "Hatchback", icon: "hatchback-icon" },
        { id: "coupe", name: "Coupe", icon: "coupe-icon" },
    ];

    function filterByCategory(categoryId) {
        navigate(`/filter?category=${categoryId}`);
    }
</script>

<div class="category-filters">
    {#each categories as category}
        <a href={`/filter?category=${category.id}`} class="category-btn">
            <div class="category-icon">
                <!-- You can replace this with actual SVG icons or images -->
                <div class={`icon ${category.icon}`}></div>
            </div>
            <span>{category.name}</span>
        </a>
    {/each}
</div>

<style>
    .category-filters {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 1rem;
    }

    .category-btn {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-decoration: none;
        color: var(--dark-gray);
        transition: transform 0.2s ease;
        width: 100px;
    }

    .category-btn:hover {
        transform: translateY(-5px);
    }

    .category-icon {
        background-color: var(--light-gray);
        width: 70px;
        height: 70px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 0.5rem;
    }

    .icon {
        width: 40px;
        height: 40px;
        background-position: center;
        background-repeat: no-repeat;
        background-size: contain;
    }

    .sedan-icon {
        background-image: url("/icons/sedan_icon.svg");
    }

    .suv-icon {
        background-image: url("/icons/suv_icon.svg");
    }
    .hatchback-icon {
        background-image: url("/icons/hatchback_icon.svg");
    }
    .coupe-icon {
        background-image: url("/icons/coupe_icon.svg");
    }

</style>