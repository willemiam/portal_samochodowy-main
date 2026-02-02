<script>
  import { onMount } from "svelte";
  import { Link } from "svelte-routing";
  import { experimentsList, isLoading, error } from "../stores/store";
  import { getExperiments } from "../lib/experimentsApi";

  let experiments = [];

  onMount(async () => {
    try {
      isLoading.set(true);
      const data = await getExperiments();
      experiments = data;
      experimentsList.set(data);
    } catch (err) {
      error.set(err.message);
    } finally {
      isLoading.set(false);
    }
  });
</script>

<svelte:head>
  <title>A/B Testing Dashboard</title>
</svelte:head>

<div class="dashboard">
  <div class="hero">
    <div class="hero-content">
      <h1>A/B Testing Dashboard</h1>
      <p>Compare LLM performance on Polish car advertisement gap-filling</p>
      <Link to="/experiments" class="btn btn-primary">
        Create New Experiment
      </Link>
    </div>
  </div>

  <div class="container">
    {#if $isLoading}
      <div class="loading">Loading experiments...</div>
    {:else if $error}
      <div class="error-message">{$error}</div>
    {:else}
      <div class="experiments-section">
        <h2>Recent Experiments</h2>
        
        {#if experiments.length === 0}
          <div class="empty-state">
            <p>No experiments yet. Create your first one!</p>
            <Link to="/experiments" class="btn btn-primary">
              Start Experiment
            </Link>
          </div>
        {:else}
          <div class="experiments-grid">
            {#each experiments as exp (exp.id)}
              <div class="experiment-card">
                <h3>{exp.name}</h3>
                {#if exp.description}
                  <p class="description">{exp.description}</p>
                {/if}
                <div class="card-meta">
                  <span class="models">
                    <strong>Models:</strong> {exp.models.join(", ")}
                  </span>
                  <span class="date">
                    {new Date(exp.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div class="card-actions">
                  <Link
                    to={`/experiments/${exp.id}`}
                    class="btn btn-outline"
                  >
                    View Results
                  </Link>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    {/if}
  </div>
</div>


<style>
  .dashboard {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  .hero {
    background: linear-gradient(135deg, var(--primary-color), #004d80);
    color: white;
    padding: 4rem 2rem;
    text-align: center;
  }

  .hero-content h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
  }

  .hero-content p {
    font-size: 1.1rem;
    margin-bottom: 2rem;
    opacity: 0.9;
  }

  .container {
    flex: 1;
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
    padding: 2rem;
  }

  .experiments-section h2 {
    font-size: 1.8rem;
    margin-bottom: 2rem;
    color: var(--dark-gray);
  }

  .experiments-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1.5rem;
  }

  .experiment-card {
    background: white;
    border: 1px solid var(--mid-gray);
    border-radius: 8px;
    padding: 1.5rem;
    transition: all 0.3s ease;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  .experiment-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
  }

  .experiment-card h3 {
    font-size: 1.3rem;
    margin-bottom: 0.5rem;
    color: var(--primary-color);
  }

  .experiment-card .description {
    color: #666;
    font-size: 0.9rem;
    margin-bottom: 1rem;
    line-height: 1.4;
  }

  .card-meta {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--light-gray);
    font-size: 0.85rem;
  }

  .card-meta .models {
    color: var(--accent-color);
    font-weight: 500;
  }

  .card-meta .date {
    color: #999;
  }

  .card-actions {
    display: flex;
    gap: 0.5rem;
  }

  .empty-state {
    text-align: center;
    padding: 3rem 1rem;
  }

  .empty-state p {
    font-size: 1.1rem;
    color: #666;
    margin-bottom: 2rem;
  }

  .loading,
  .error-message {
    text-align: center;
    padding: 2rem;
    font-size: 1rem;
  }

  .error-message {
    color: var(--danger);
    background-color: #ffe6e6;
    border-radius: 4px;
    padding: 1rem;
  }

  @media (max-width: 768px) {
    .hero-content h1 {
      font-size: 1.8rem;
    }

    .experiments-grid {
      grid-template-columns: 1fr;
    }
  }
</style>