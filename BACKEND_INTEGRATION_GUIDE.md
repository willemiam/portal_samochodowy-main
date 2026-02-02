# Backend Integration Guide: A/B Testing Frontend Ready

**Frontend Status:** ✅ Complete  
**Branch:** `studzinsky/feature/ab-testing`  
**Entry Point:** `http://localhost:5173`

---

## Quick Overview

The frontend has been completely redesigned from a car marketplace portal to an A/B testing visualization dashboard. **No user authentication**, **no car data**, just pure **experiment comparison**.

---

## API Endpoints Required

The frontend calls these endpoints. Your backend must implement them:

### **1. Experiment Creation & List**

```bash
POST /api/experiments
Content-Type: application/json

{
  "name": "Bielik vs Llama",
  "description": "Compare two models on 10 car ads",
  "models": ["bielik-1.5b-gguf", "llama-3.1-8b"],
  "parameters": {
    "temperature": 0.3,
    "max_tokens": 256,
    "gap_notation": "auto"
  }
}

# Response:
{
  "id": "exp_123abc",
  "name": "Bielik vs Llama",
  "description": "Compare two models on 10 car ads",
  "models": ["bielik-1.5b-gguf", "llama-3.1-8b"],
  "parameters": { ... },
  "created_at": "2026-02-03T10:00:00Z",
  "created_by": null  # (no users, can be null or hardcoded)
}
```

```bash
GET /api/experiments

# Response:
[
  { id: "exp_123abc", name: "Bielik vs Llama", ... },
  { id: "exp_456def", name: "Bielik 1.5B Test", ... }
]
```

---

### **2. Running an Experiment**

```bash
POST /api/experiments/<id>/run
Content-Type: application/json

{
  "items": [
    {
      "id": "item-1",
      "text_with_gaps": "Sprzedam [GAP:1] BMW w [GAP:2] stanie"
    },
    {
      "id": "item-2",
      "text_with_gaps": "Auto ma ___ km przebiegu i ___ lakier"
    }
  ]
}

# Response:
{
  "results": [
    {
      "id": "run_789ghi",
      "experiment_id": "exp_123abc",
      "item_id": "item-1",
      "model_name": "bielik-1.5b-gguf",
      "original_text": "Sprzedam [GAP:1] BMW w [GAP:2] stanie",
      "filled_text": "Sprzedam piękne BMW w dobrym stanie",
      "gaps": [
        {
          "index": 1,
          "marker": "[GAP:1]",
          "choice": "piękne",
          "alternatives": ["zadbane", "eleganckie"]
        },
        {
          "index": 2,
          "marker": "[GAP:2]",
          "choice": "dobrym",
          "alternatives": ["doskonałym", "świetnym"]
        }
      ],
      "semantic_score": 0.85,
      "domain_score": 0.90,
      "grammar_score": 0.95,
      "overall_score": 0.90,
      "generation_time": 2.3
    },
    // ... more results (one per model × one per item)
  ]
}
```

---

### **3. Fetching Results**

```bash
GET /api/experiments/<id>/results

# Response:
{
  "experiment_id": "exp_123abc",
  "experiment_name": "Bielik vs Llama",
  "models_compared": ["bielik-1.5b-gguf", "llama-3.1-8b"],
  "total_items": 2,
  "results": [ ... ],  # Same array as /run response above
  "created_at": "2026-02-03T10:00:00Z"
}
```

---

### **4. Export Results**

```bash
GET /api/experiments/<id>/export?format=csv

# Returns: CSV file download with all results
```

---

### **5. Available Models**

```bash
GET /api/models

# Response:
[
  { "name": "bielik-1.5b-gguf" },
  { "name": "bielik-11b-gguf" },
  { "name": "llama-3.1-8b" },
  { "name": "qwen2.5-3b" }
]
```

---

### **6. Delete Experiment**

```bash
DELETE /api/experiments/<id>

# Response:
{ "status": "deleted" }
```

---

## Key Design Decisions

1. **No User Context**
   - All experiments are "anonymous"
   - `created_by` can be `null` or ignored
   - No login/auth required
   - This is a **research/demo tool**, not production

2. **Flexible Scoring**
   - Frontend doesn't validate score ranges
   - Just displays what backend returns
   - Scores can be: 0-1 (normalized), 0-100 (percentage), or any other scale
   - Frontend will just format to 2 decimal places

3. **Gap Notation Support**
   - Frontend accepts: `[GAP:1]`, `[GAP:2]`, ... or `___`
   - Backend can standardize to either format before processing
   - Frontend's "gap_notation" parameter is just a hint to backend

4. **Model Flexibility**
   - Any model name works (doesn't validate against known models)
   - `getAvailableModels()` just populates the checkbox list
   - Backend can add new models anytime

---

## Frontend API Client Location

**File:** `portal_samochodowy-main/frontend/src/lib/experimentsApi.js`

All HTTP calls are centralized here:
- `createExperiment(experiment)`
- `getExperiments()`
- `getExperiment(experimentId)`
- `runExperiment(experimentId, testItems)`
- `getExperimentResults(experimentId)`
- `exportResults(experimentId, format)`
- `deleteExperiment(experimentId)`
- `getAvailableModels()`

**Base URL:**
- From env: `VITE_API_URL` or
- Fallback: `http://localhost:5000/api`

---

## Frontend Routes

| Route | Purpose |
|-------|---------|
| `/` | Dashboard - list recent experiments |
| `/experiments` | Create new experiment + view results |
| `/experiments/<id>` | Detailed results for experiment |

---

## State Management

**File:** `portal_samochodowy-main/frontend/src/stores/store.ts`

Global state stores (Svelte writable):
- `selectedExperiment` - Currently editing/viewing experiment config
- `experimentResults` - Results from last experiment run
- `experimentsList` - List of all experiments
- `isLoading` - Boolean for pending requests
- `error` - Error message string

---

## Expected Timeline

- **Now:** Frontend deployed, ready for API testing
- **Next:** Backend implements `/api/experiments/*` endpoints
- **Testing:** Frontend + Backend integration tests
- **Demo:** Live A/B testing on Portal with real Bielik/Llama models

---

## Environment Variables

The frontend needs one optional env var:

```bash
# .env (in frontend folder)
VITE_API_URL=http://localhost:5000

# If not set, defaults to http://localhost:5000
```

For HF Space deployment, use:
```bash
VITE_API_URL=https://your-backend-url.com
```

---

## Database Schema Hint

(For backend developers) - The backend likely needs tables like:

```sql
CREATE TABLE experiments (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  models JSON,  -- ["model1", "model2"]
  parameters JSON,  -- {temperature, max_tokens, gap_notation}
  created_at TIMESTAMP,
  created_by TEXT -- NULL if no auth
);

CREATE TABLE experiment_results (
  id TEXT PRIMARY KEY,
  experiment_id TEXT,
  item_id TEXT,
  model_name TEXT,
  original_text TEXT,
  filled_text TEXT,
  gaps JSON,  -- [{index, marker, choice, alternatives}]
  semantic_score FLOAT,
  domain_score FLOAT,
  grammar_score FLOAT,
  overall_score FLOAT,
  generation_time FLOAT,
  FOREIGN KEY (experiment_id) REFERENCES experiments(id)
);
```

---

## Common Issues & Solutions

### **Issue:** "Cannot GET /api/experiments"
**Solution:** Backend endpoint not implemented. Check FastAPI/Flask routes.

### **Issue:** Frontend shows "No experiments"
**Solution:** Normal if none created yet. Try creating one via form.

### **Issue:** Models dropdown is empty
**Solution:** `/api/models` not implemented or returning wrong format.

### **Issue:** Results table shows "undefined"
**Solution:** Backend not returning required fields (`overall_score`, `generation_time`, etc.). Check response structure.

### **Issue:** Export doesn't download
**Solution:** `/api/experiments/<id>/export` not implemented or not returning file blob.

---

## Success Criteria

✅ Dashboard loads
✅ Can list experiments (even if empty)
✅ Can create experiment
✅ Can select models (from `/api/models`)
✅ Can run experiment (calls `/api/experiments/<id>/run`)
✅ Results display in table
✅ Can view experiment detail page
✅ Can export to CSV

---

**Ready to integrate?** Start with implementing the 7 endpoints above, then test with the frontend at `localhost:5173`.

