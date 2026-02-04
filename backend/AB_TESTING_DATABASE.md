# A/B Testing Database Implementation - Complete Guide

## ✅ What Was Implemented

### 1. **Database Models** (backend/models.py)
Three new SQLAlchemy models added to track A/B testing:

#### **Experiment Model**
Represents a single A/B test comparing multiple LLMs.

```python
class Experiment:
    - id (Primary Key)
    - name: str              # Test name
    - description: str       # What you're testing
    - models: JSON          # ["bielik-1.5b-gguf", "llama-3.1-8b"]
    - parameters: JSON      # {temperature: 0.3, max_tokens: 200}
    - test_ads: JSON        # [1, 2, 3, 4, 5]
    - status: str           # pending, running, completed, failed
    - total_runs: int       # Total LLM calls made
    - completed_runs: int   # Successful completions
    - failed_runs: int      # Failed generations
    - created_at: DateTime
    - started_at: DateTime
    - completed_at: DateTime
    - notes: str            # Research notes
```

#### **ExperimentRun Model**
Individual LLM output for one ad with one model.

```python
class ExperimentRun:
    - id (Primary Key)
    - experiment_id: FK     # Which experiment
    - model_name: str       # Which model generated this
    - ad_id: int            # Which test ad
    - original_text: str    # Original with [GAP:n] markers
    - filled_text: str      # LLM output
    - gap_fills: JSON       # {1: {choice: "word", alternatives: [...]}}
    - semantic_score: float # 0-1
    - domain_relevance_score: float  # 0-1
    - grammar_score: float  # 0-1
    - overall_score: float  # 0-1
    - generation_time: float # Seconds
    - status: str           # success, error, invalid_output
    - error_message: str    # If failed
    - created_at: DateTime
```

#### **QualityEvaluation Model**
Optional human evaluation of results.

```python
class QualityEvaluation:
    - id (Primary Key)
    - experiment_id: FK
    - run_id: FK            # Links to ExperimentRun
    - human_rating: int     # 1-5 stars
    - human_notes: str
    - gap_feedback: JSON    # {1: "correct", 2: "incorrect"}
    - is_valid: bool        # JSON valid, gaps filled
    - has_errors: bool
    - error_details: str
    - evaluated_by: str     # Evaluator identifier
    - created_at: DateTime
```

### 2. **Metrics Module** (backend/metrics.py)
Calculates quality scores automatically.

```python
class GapFillMetrics:
    - calculate_semantic_score()       # Word validity (0-1)
    - calculate_domain_relevance_score() # Car vocabulary match (0-1)
    - calculate_grammar_score()        # Polish case agreement (0-1)
    - calculate_overall_score()        # Weighted average
    - evaluate_gap_fill()              # Single gap evaluation
    - evaluate_multiple_fills()        # Batch evaluation
```

**Scoring Logic:**
- **Semantic** (35% weight): Word length, vowels, Polish patterns, case, no obvious errors
- **Domain Relevance** (40% weight): Matches car vocabulary (colors, conditions, engines, features)
- **Grammar** (25% weight): Polish case agreement (nominative, instrumental, genitive, etc.)

### 3. **API Endpoints** (backend/routes.py)
Added 6 REST endpoints for A/B testing:

```
GET    /api/experiments                    → List all experiments
POST   /api/experiments                    → Create new experiment
GET    /api/experiments/<id>               → Get experiment details
PUT    /api/experiments/<id>               → Update experiment
DELETE /api/experiments/<id>               → Delete experiment
GET    /api/experiments/<id>/runs          → List all runs for experiment
POST   /api/experiments/<id>/runs          → Add new run result
GET    /api/experiments/<id>/results       → Get aggregated statistics
GET    /api/experiments/<id>/export        → Download results as CSV
GET    /api/experiments/<id>/evaluations   → List quality evaluations
POST   /api/experiments/<id>/evaluations   → Add new evaluation
```

### 4. **Database Initialization** (backend/init_ab_testing.py)
Script to create tables and verify schema.

---

## 📊 Database Schema Diagram

```
┌─────────────────────────────────────────────────────────┐
│ Experiment (1 test)                                     │
├─────────────────────────────────────────────────────────┤
│ id, name, description                                   │
│ models: ["bielik-1.5b", "llama-3.1"]                   │
│ test_ads: [1, 2, 3, 4, 5]                              │
│ status: "running"                                       │
│ total_runs: 10, completed_runs: 8, failed_runs: 2     │
└─────────────────────────────────────────────────────────┘
            ↓ 1:N relationship
        ╔═══════════════════════════════════════╗
        ║                                       ║
┌───────────────────────────────┐    ┌──────────────────────────────┐
│ ExperimentRun (1 model × 1 ad)│    │ QualityEvaluation (human)    │
├───────────────────────────────┤    ├──────────────────────────────┤
│ model_name: "bielik-1.5b"    │    │ human_rating: 5              │
│ ad_id: 1                      │    │ human_notes: "Perfect!"      │
│ original_text: "..."          │    │ gap_feedback: {1: "correct"}│
│ filled_text: "..."            │    │ is_valid: true              │
│ overall_score: 0.87           │    │ evaluated_by: "user@..."     │
└───────────────────────────────┘    └──────────────────────────────┘
        10 runs total                  (optional, for validation)
```

---

## 🚀 How to Use

### Step 1: Initialize Database
```bash
cd backend
python init_ab_testing.py
```

Output:
```
✅ Tables created successfully!
  ✓ experiments table exists
  ✓ experiment_runs table exists
  ✓ quality_evaluations table exists

✨ Database initialization complete!
✅ Sample experiment created!
   ID: 1, Name: Sample A/B Test
```

### Step 2: Create an Experiment
```bash
curl -X POST http://localhost:5000/api/experiments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First A/B Test",
    "description": "Comparing Bielik 1.5B vs Llama 3.1 on 20 car ads",
    "models": ["bielik-1.5b-gguf", "llama-3.1-8b"],
    "parameters": {
      "temperature": 0.3,
      "max_tokens": 200,
      "grammar_enabled": true
    },
    "test_ads": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "notes": "Testing with grammar constraints"
  }'
```

Response:
```json
{
  "id": 1,
  "name": "My First A/B Test",
  "status": "pending",
  "totalRuns": 0,
  "completedRuns": 0,
  "failedRuns": 0,
  "createdAt": "2026-02-02 10:30:00"
}
```

### Step 3: Add Run Results (from Bielik service)
```bash
curl -X POST http://localhost:5000/api/experiments/1/runs \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "bielik-1.5b-gguf",
    "ad_id": 1,
    "original_text": "Sprzedam [GAP:1] BMW w [GAP:2] stanie",
    "filled_text": "Sprzedam eleganckie BMW w doskonałym stanie",
    "gap_fills": {
      "1": {"choice": "eleganckie", "alternatives": ["piękne", "zadbane"]},
      "2": {"choice": "doskonałym", "alternatives": ["bardzo dobrym"]}
    },
    "semantic_score": 0.85,
    "domain_relevance_score": 0.92,
    "grammar_score": 0.88,
    "overall_score": 0.88,
    "generation_time": 2.34,
    "status": "success"
  }'
```

### Step 4: View Results
```bash
curl http://localhost:5000/api/experiments/1/results
```

Response:
```json
{
  "experimentId": 1,
  "experimentName": "My First A/B Test",
  "status": "pending",
  "totalRuns": 2,
  "modelStats": {
    "bielik-1.5b-gguf": {
      "total_runs": 1,
      "successful_runs": 1,
      "avg_overall_score": 0.88,
      "avg_generation_time": 2.34
    },
    "llama-3.1-8b": {
      "total_runs": 1,
      "successful_runs": 1,
      "avg_overall_score": 0.82,
      "avg_generation_time": 1.89
    }
  }
}
```

### Step 5: Export Results
```bash
curl http://localhost:5000/api/experiments/1/export > results.csv
```

---

## 📋 Example: Complete A/B Test Workflow

### Scenario: Compare 2 models on 5 test ads

**1. Prepare test ads** (should already exist in Items table)
```python
test_ads = [101, 102, 103, 104, 105]  # Item IDs
```

**2. Create experiment**
```json
{
  "name": "Thesis Test - Bielik vs Llama",
  "description": "Compare gap-filling quality on polish car ads",
  "models": ["bielik-1.5b-gguf", "llama-3.1-8b"],
  "test_ads": [101, 102, 103, 104, 105],
  "parameters": {"temperature": 0.3, "max_tokens": 200}
}
```

**3. Run experiment** (pseudocode)
```python
for ad_id in [101, 102, 103, 104, 105]:
    for model in ["bielik-1.5b-gguf", "llama-3.1-8b"]:
        # 1. Get original ad with gaps
        original_text = get_ad(ad_id).description
        
        # 2. Call Bielik service
        response = call_bielik_infill(
            text=original_text,
            model=model,
            temperature=0.3
        )
        
        # 3. Calculate metrics
        scores = GapFillMetrics.evaluate_multiple_fills(
            fills=[...gap fills...]
        )
        
        # 4. Store result
        POST /api/experiments/{exp_id}/runs {
            model_name: model,
            ad_id: ad_id,
            filled_text: response.filled_text,
            overall_score: scores.average_overall,
            ...
        }
```

**4. Analyze results**
```bash
# Get statistics
GET /api/experiments/1/results

# Export for thesis
GET /api/experiments/1/export

# Manual evaluation (optional)
POST /api/experiments/1/evaluations {
    run_id: 1,
    human_rating: 5,
    human_notes: "Perfect gap fill!"
}
```

---

## 📂 Files Modified/Created

```
backend/
├── models.py                    # ✅ Added: Experiment, ExperimentRun, QualityEvaluation
├── metrics.py                   # ✅ Created: GapFillMetrics class
├── routes.py                    # ✅ Added: 6 A/B testing endpoints
├── init_ab_testing.py          # ✅ Created: Database initialization script
└── vehicles.db                  # Auto-created: SQLite database
```

---

## 🧪 Testing Locally

### Option 1: Using curl
```bash
# 1. Start Portal backend
cd backend
python app.py

# 2. In another terminal, create experiment
curl -X POST http://localhost:5000/api/experiments \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "models": ["model1"], "test_ads": [1,2,3]}'

# 3. View results
curl http://localhost:5000/api/experiments/1
```

### Option 2: Using Python
```python
import requests

# Create experiment
response = requests.post('http://localhost:5000/api/experiments', json={
    'name': 'Test',
    'models': ['bielik-1.5b-gguf'],
    'test_ads': [1, 2, 3]
})
exp_id = response.json()['id']

# Add run
requests.post(f'http://localhost:5000/api/experiments/{exp_id}/runs', json={
    'model_name': 'bielik-1.5b-gguf',
    'ad_id': 1,
    'original_text': 'Ad with [GAP:1] marker',
    'filled_text': 'Ad with word marker',
    'gap_fills': {'1': {'choice': 'word'}},
    'overall_score': 0.85
})

# View results
results = requests.get(f'http://localhost:5000/api/experiments/{exp_id}/results')
print(results.json())
```

### Option 3: Using Docker
```bash
cd local_deployment
docker-compose up

# Database will be initialized automatically
# Visit http://localhost:5000/api/experiments
```

---

## 📊 Metrics Scoring Example

**Input:** Gap fill from Bielik for ad "Fiat 500 [GAP:1] z [GAP:2] silnikiem"

**Gap 1: "biały" (white)**
```
Semantic Score:    0.92 (valid Polish word, proper case)
Domain Relevance:  0.95 (color in car vocabulary)
Grammar Score:     0.88 (nominative correct)
Overall:           0.92 (excellent)
```

**Gap 2: "benzynowy" (gasoline)**
```
Semantic Score:    0.90
Domain Relevance:  0.98 (engine type, perfect match)
Grammar Score:     0.85 (should be "benzynowym" instrumental - caught!)
Overall:           0.91 (good - grammar could be fixed)
```

**Run Average:**
```
Average Overall:   0.915 (91.5% quality)
Quality Level:     "excellent"
```

---

## ⚡ Next Steps

### Phase 4 (Frontend) - Estimated Week 3-4
- Create Svelte components for UI
- Display experiment results
- Show comparison charts

### Integration with Bielik Service
- Set up automated runner to call Bielik API
- Store results in database
- Calculate metrics

### Thesis Analysis
- Run experiment on 50+ ads
- Compare 3 models statistically
- Generate graphs for defense

---

## 🔍 Troubleshooting

### Issue: "Table already exists"
```python
# Drop and recreate
python
>>> from app import db, create_app
>>> app = create_app()
>>> with app.app_context():
...     db.drop_all()
...     db.create_all()
```

### Issue: Foreign key errors
Ensure Items table exists before adding experiment runs.

### Issue: Missing metrics scores
Manually calculate using `GapFillMetrics` after adding run:
```python
from metrics import GapFillMetrics
result = GapFillMetrics.evaluate_multiple_fills([...])
```

---

## 📚 Database Relationships

```
Items (existing car ads)
    ↓ (one-to-many)
Experiment
    ├→ ExperimentRun (10 runs: 2 models × 5 ads)
    │   └→ QualityEvaluation (optional human rating)
    └→ QualityEvaluation
```

---

## ✨ Summary

You now have:
✅ Three database tables for A/B testing
✅ Automatic metric calculation (35% code)
✅ Six REST API endpoints
✅ CSV export functionality
✅ Sample experiment setup
✅ Complete documentation

**Status: Ready for Phase 4 (Frontend)**

