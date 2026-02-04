# Frontend Architecture: A/B Testing Redesign

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Portal A/B Testing Frontend                        │
│                         (studzinsky/feature/ab-testing)                     │
└─────────────────────────────────────────────────────────────────────────────┘

                                  http://localhost:5173
                                          │
              ┌─────────────────────────────┼──────────────────────────────┐
              │                             │                              │
         ┌────▼────┐                   ┌────▼────┐                   ┌────▼────┐
         │   /     │                   │/exp...  │                   │ /exp/:id│
         │Dashboard│                   │Creator  │                   │ Details │
         └────┬────┘                   └────┬────┘                   └────┬────┘
              │                             │                             │
              │ home.svelte                 │ experiments.svelte          │experimentDetail.svelte
              │ (Dashboard)                 │ (Form + Results)            │ (Detail View)
              │                             │                             │
              └─────────────────────────────┼─────────────────────────────┘
                                            │
                   ┌────────────────────────┼────────────────────────────┐
                   │                        │                            │
              ┌────▼────────┐         ┌─────▼──────┐         ┌──────▼────┐
              │   Navbar    │         │   Footer   │         │   Forms   │
              │ (simplified)│         │ (standard) │         │  & Tables │
              └─────────────┘         └────────────┘         └───────────┘
                        │                                          │
                        └──────────────────┬───────────────────────┘
                                          │
                         ┌────────────────▼─────────────────┐
                         │    State Management (Svelte)     │
                         │  (stores/store.ts)               │
                         └────────────────┬─────────────────┘
                                          │
           ┌──────────────────────────────┼──────────────────────────────┐
           │                              │                              │
    ┌──────▼──────┐              ┌────────▼────────┐          ┌──────────▼───┐
    │selectedExp  │              │experimentResults│          │experiments   │
    │Config       │              │(null or data)   │          │List          │
    └─────────────┘              └─────────────────┘          └──────────────┘
           │                              │                              │
           │ (current form)               │ (last run)                   │ (from DB)
           │                              │                              │
           └──────────────┬───────────────┴──────────────────────────────┘
                          │
              ┌───────────▼────────────┐
              │  Error & Loading State │
              │  (isLoading, error)    │
              └───────────┬────────────┘
                          │
           ┌──────────────▼──────────────┐
           │   API Client Layer          │
           │ (lib/experimentsApi.js)     │
           │                             │
           │ ✓ createExperiment()        │
           │ ✓ getExperiments()          │
           │ ✓ runExperiment()           │
           │ ✓ getExperimentResults()    │
           │ ✓ exportResults()           │
           │ ✓ deleteExperiment()        │
           │ ✓ getAvailableModels()      │
           └──────────────┬──────────────┘
                          │
                 Base URL: http://localhost:5000
                          │
           ┌──────────────▼──────────────┐
           │    Backend API Endpoints    │
           │  (/api/experiments/*)       │
           │                             │
           │ POST   /api/experiments     │
           │ GET    /api/experiments     │
           │ GET    /api/experiments/<id>│
           │ POST   /api/experiments/<id>│/run
           │ GET    /api/experiments/<id>│/results
           │ GET    /api/experiments/<id>│/export
           │ DELETE /api/experiments/<id>│
           │ GET    /api/models          │
           └─────────────────────────────┘
                          │
           ┌──────────────▼──────────────┐
           │    Database Layer           │
           │ (SQLite in Portal)          │
           │                             │
           │ • experiments table         │
           │ • experiment_results table  │
           └─────────────────────────────┘
```

---

## Data Flow Example: Creating & Running Experiment

```
User fills form:
  Name: "Bielik vs Llama"
  Models: [checkbox] bielik-1.5b, [checkbox] llama-3.1
  Temperature: 0.3
  Items: ["Sprzedam [GAP:1]...", "Auto ma ___..."]
        │
        ▼
  Form Validation ✓
        │
        ▼
  experientsApi.createExperiment(config)
        │
        ├─► POST /api/experiments
        │
        ▼
  Backend creates record, returns {id: "exp_123"}
        │
        ▼
  Store: selectedExperiment = {id, name, models, ...}
        │
        ▼
  experimentsApi.runExperiment(exp_123, items)
        │
        ├─► POST /api/experiments/exp_123/run
        │
        ▼
  Backend processes:
    ├─ For each model + each item
    ├─ Send to Bielik/Llama inference
    ├─ Collect results with scores
    ├─ Calculate semantic/domain/grammar scores
    └─ Return all results
        │
        ▼
  Store: experimentResults = {results: [...]}
        │
        ▼
  Component renders ResultsTable
        │
        ├─ Shows: original_text | filled_text | scores | time
        ├─ Groups by model
        ├─ Calculates averages
        └─ Shows alternatives
        │
        ▼
  User can:
    • View detailed results page (/experiments/exp_123)
    • Export to CSV
    • Create another experiment
    • Delete this experiment
```

---

## Component Hierarchy

```
App.svelte (root)
│
├── Navbar.svelte
│   └── [simplified, no auth]
│
├── Router
│   │
│   ├── Route(/) → home.svelte (Dashboard)
│   │   │
│   │   └── Displays:
│   │       ├─ Hero section
│   │       └─ Experiments grid (from store)
│   │
│   ├── Route(/experiments) → experiments.svelte (Creator)
│   │   │
│   │   └── Displays:
│   │       ├─ ExperimentForm
│   │       │   ├─ Name + Description
│   │       │   ├─ Model checkboxes
│   │       │   ├─ Parameter sliders
│   │       │   └─ Test item input
│   │       │
│   │       └─ OR ResultsDisplay (after run)
│   │           ├─ Results table
│   │           └─ Model comparison
│   │
│   └── Route(/experiments/:id) → experimentDetail.svelte (Details)
│       │
│       └── Displays:
│           ├─ Summary cards
│           ├─ Full results table
│           ├─ Gap analysis
│           ├─ Export button
│           └─ Delete button
│
└── Footer.svelte
    └── [standard, no changes]
```

---

## State Tree

```
store.ts (Svelte Stores)
│
├── selectedExperiment: ExperimentConfig | null
│   ├─ id?: string
│   ├─ name: string
│   ├─ description?: string
│   ├─ models: string[] (["bielik-1.5b", "llama-3.1"])
│   ├─ parameters: {
│   │  ├─ temperature: number (0-1)
│   │  ├─ max_tokens: number (50-512)
│   │  └─ gap_notation: string ("auto" | "[GAP:n]" | "___")
│   │ }
│   ├─ created_at?: string
│   └─ created_by?: string
│
├── experimentResults: ExperimentResult | null
│   ├─ experiment_id: string
│   ├─ experiment_name: string
│   ├─ models_compared: string[]
│   ├─ total_items: number
│   ├─ results: ExperimentRunResult[] (one per model × item)
│   │   └─ ExperimentRunResult {
│   │      ├─ id?: string
│   │      ├─ experiment_id?: string
│   │      ├─ item_id: string ("item-1")
│   │      ├─ model_name: string ("bielik-1.5b")
│   │      ├─ original_text: string
│   │      ├─ filled_text: string
│   │      ├─ gaps: GapResult[]
│   │      │   └─ { index, marker, choice, alternatives[] }
│   │      ├─ semantic_score?: number
│   │      ├─ domain_score?: number
│   │      ├─ grammar_score?: number
│   │      ├─ overall_score?: number (weighted avg)
│   │      └─ generation_time?: number (seconds)
│   │ }
│   └─ created_at?: string
│
├── experimentsList: ExperimentConfig[]
│   └─ Array of all experiments from DB
│
├── isLoading: boolean
│   └─ True while API call in progress
│
└── error: string | null
    └─ Error message if API call fails
```

---

## CSS Design System

```
Color Tokens:
  --primary-color: #1a3353 (dark blue)
  --accent-color: #0088cc (bright blue)
  --accent-hover: #006699 (darker blue)
  --light-gray: #f8f9fa (page bg)
  --mid-gray: #e9ecef (borders)
  --dark-gray: #333333 (text)
  --success: #28a745
  --warning: #ffc107
  --danger: #dc3545

New A/B Testing Colors:
  --chart-blue: #3b82f6
  --chart-green: #10b981
  --chart-purple: #8b5cf6
  --chart-orange: #f97316
  --stat-good: #22c55e
  --stat-fair: #f59e0b
  --stat-poor: #ef4444

Button Classes:
  .btn (base)
  .btn-primary (blue, white text)
  .btn-outline (border, transparent)
  .btn-outline:disabled (50% opacity)

Card Classes:
  .card (white bg, shadow, hover lift)
  .comparison-card (border, hover shadow)

Metric Classes:
  .metric-badge.good (green)
  .metric-badge.fair (orange)
  .metric-badge.poor (red)
  .metric-badge.neutral (gray)

Result Classes:
  .result-better (green bg)
  .result-worse (red bg)
  .result-same (transparent)

Alert Classes:
  .alert-success (green)
  .alert-warning (orange)
  .alert-danger (red)
  .alert-info (blue)
```

---

## File Organization

```
frontend/src/
│
├── App.svelte                      [Root component, router setup]
├── main.ts                         [Entry point]
├── app.css                         [Global styles + design tokens]
├── vite-env.d.ts                   [TypeScript declarations]
├── auth_config.ts                  [DELETED]
├── authService.ts                  [DELETED]
│
├── routes/                         [Page-level components]
│   ├── home.svelte                 [Dashboard - modified]
│   ├── experiments.svelte          [Experiment creator - NEW]
│   ├── experimentDetail.svelte     [Results detail - NEW]
│   ├── filter.svelte               [Can be repurposed or deleted]
│   ├── addItem.svelte              [UNUSED - safe to delete]
│   ├── account.svelte              [UNUSED - safe to delete]
│   └── items.svelte                [UNUSED - safe to delete]
│
├── components/                     [Reusable UI components]
│   ├── Navbar.svelte               [Modified - auth removed]
│   ├── Footer.svelte               [No changes needed]
│   ├── PhotoGrid.svelte            [UNUSED - safe to delete]
│   ├── CarCard.svelte              [UNUSED - safe to delete]
│   ├── CategoryFilter.svelte       [UNUSED - safe to delete]
│   ├── MainBanner.svelte           [UNUSED - safe to delete]
│   └── Counter.svelte              [Test artifact]
│
├── lib/                            [Utilities]
│   ├── experimentsApi.js           [API client - NEW]
│   ├── api.js                      [OLD car API - can delete]
│   └── Counter.svelte              [Test file]
│
└── stores/                         [State management]
    └── store.ts                    [Svelte stores - modified]
```

---

## Environment Setup

```
.env (frontend/.env)
─────────────────────
VITE_API_URL=http://localhost:5000
VITE_APP_TITLE=A/B Testing Dashboard

OR for HF Space:
VITE_API_URL=https://your-backend-url.com
```

---

## Build & Deploy

```
Development:
  npm run dev       → http://localhost:5173

Production:
  npm run build     → dist/ folder
  npm run preview   → Preview production build

Docker (if needed):
  docker build -t portal-frontend .
  docker run -p 5173:5173 portal-frontend
```

---

**Status:** ✅ COMPLETE & READY FOR INTEGRATION
