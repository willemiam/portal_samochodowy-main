# LLM Description Enhancer Platform Investigation

## Current Architecture Analysis

### Tech Stack
- **Backend**: Flask + SQLAlchemy + SQLite
- **Frontend**: Svelte + Vite
- **AI Integration**: FastAPI microservice (HuggingFace Bielik model on port 8000)
- **Storage**: Local/AWS S3 via StorageService abstraction
- **Auth**: Auth0 (optional, dev mode available)

### Existing Models
1. **Category**: Flexible categorization system (already multi-domain ready)
2. **CategorySchema**: Dynamic field definitions per category (JSON-based)
3. **Product**: Generic product abstraction
4. **Car**: Specific car domain model
5. **Items**: Listings with descriptions, photos, attributes (JSON)
6. **Users**: User management
7. **Photo**: Multi-photo support with storage abstraction

### Current AI Integration
- External FastAPI service on port 8000
- Endpoint: `/enhance-description`
- Input: CarData schema (make, model, year, mileage, features[], condition)
- Output: Enhanced Polish description
- Integration: Frontend calls AI service directly
- Status: Optional, graceful degradation if unavailable

## MCP (Model Context Protocol) Integration

### What is MCP?
MCP = standardized protocol for AI model communication & context management
Enables:
- Structured context passing
- Multi-model orchestration
- Context persistence across sessions
- Tool/function calling capabilities

### Integration Strategy
**Option 1: MCP Server Layer** (Recommended)
```
Frontend → Backend (Flask) → MCP Server → LLM Provider (Bielik)
                           ↓
                       Context Store (SQLite/Redis)
```

**Option 2: Direct MCP in Backend**
```
Frontend → Backend (Flask + MCP Client) → LLM Provider
                  ↓
              Context DB
```

### Implementation Plan
1. **MCP Server Setup**
   - Python MCP server library (modelcontextprotocol)
   - Endpoints: /mcp/enhance, /mcp/context
   - Context store: SQLite table or Redis

2. **Context Schema**
   ```python
   {
     "session_id": "uuid",
     "domain": "cars|apartments|...",
     "item_data": {...},
     "conversation_history": [],
     "rag_context": [],
     "user_preferences": {}
   }
   ```

3. **Backend Integration**
   - New routes: `/api/enhance-description-mcp`
   - MCP client in Flask
   - Context persistence per user session

## RAG (Retrieval-Augmented Generation) Integration

### RAG Purpose
Enhance LLM outputs with domain-specific knowledge:
- Car specs, common features, market trends
- Apartment amenities, locations, pricing patterns
- Historical listings for context
- User preferences/templates

### Multi-Domain RAG Architecture
**Option 1: Single Vector DB with Domain Filtering** (Recommended)
```
Vector DB (ChromaDB/FAISS)
├── cars_collection
│   ├── car_specs_embeddings
│   ├── successful_listings
│   └── domain_knowledge
├── apartments_collection
│   ├── location_data
│   ├── amenities_catalog
│   └── market_insights
└── general_collection
    └── writing_templates
```

**Option 2: Separate RAG per Domain**
```
RAG_Cars_Service (port 8001)
RAG_Apartments_Service (port 8002)
Common RAG Interface
```

### Implementation Plan
1. **Vector Store Selection**
   - **ChromaDB**: Lightweight, Python-native, persistent
   - **FAISS**: Fast similarity search, in-memory/disk
   - Recommendation: ChromaDB for simplicity

2. **Embedding Model**
   - Use HuggingFace sentence-transformers
   - Model: "paraphrase-multilingual-MiniLM-L12-v2" (Polish support)
   - Alternative: Bielik-based embeddings

3. **Knowledge Base Setup**
   ```python
   # Per domain collections
   cars_rag = {
     "specs": Load from final_vehicle_data.csv,
     "listings": Existing items with good descriptions,
     "domain_docs": Car terminology, features glossary
   }
   
   apartments_rag = {
     "locations": City/district data,
     "amenities": Common apartment features,
     "listings": Apartment descriptions corpus
   }
   ```

4. **RAG Service Architecture**
   ```
   /backend/services/rag_service.py
   ├── RAGService (base class)
   ├── CarRAG(RAGService)
   ├── ApartmentRAG(RAGService)
   └── get_rag_for_domain(domain) -> RAGService
   ```

5. **Retrieval Flow**
   ```
   User inputs item data
   → Extract key features
   → Query vector DB (top-k similar items)
   → Combine: user_data + rag_context + template
   → Send to LLM (via MCP)
   → Enhanced description
   ```

## Multi-Domain Platform Transformation

### Current State
- Hardcoded for cars (Car model, CarData schema)
- Category system exists but underutilized
- Items table has JSON attributes (flexible)

### Transformation Strategy

**Phase 1: Abstract Domain Logic**
1. Leverage existing Category/CategorySchema models
2. Create domain configurations:
   ```python
   DOMAIN_CONFIGS = {
     "cars": {
       "model": Car,
       "schema_fields": ["make", "model", "year", ...],
       "rag_collection": "cars_collection",
       "prompt_template": "car_enhancement_prompt"
     },
     "apartments": {
       "model": Apartment,  # new model
       "schema_fields": ["location", "rooms", "area", ...],
       "rag_collection": "apartments_collection",
       "prompt_template": "apartment_enhancement_prompt"
     }
   }
   ```

3. Generic enhancement endpoint:
   ```
   POST /api/items/enhance-description
   {
     "domain": "cars|apartments",
     "item_data": {...},
     "style": "professional|casual|detailed"
   }
   ```

**Phase 2: Domain-Specific Models**
```python
class Apartment(db.Model):
    __tablename__ = 'apartments'
    id, location, rooms, area, floor, 
    building_year, heating_type, etc.
    
class RealEstate(db.Model):  # Generic
    __tablename__ = 'real_estate'
    # Common fields
    
# Items table links to domain-specific tables
```

**Phase 3: RAG per Domain**
- Separate embeddings collections
- Domain-specific prompt engineering
- Context retrieval tuned per domain

### Architecture After Transformation

```
┌─────────────────────────────────────────────┐
│          Svelte Frontend                    │
│  (Domain-agnostic listing interface)        │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         Flask Backend API                   │
│  ┌────────────────────────────────────┐    │
│  │  Domain Router                      │    │
│  │  - /api/cars/*                      │    │
│  │  - /api/apartments/*                │    │
│  │  - /api/items/enhance (generic)     │    │
│  └────────────┬───────────────────────┘    │
│               │                             │
│  ┌────────────▼───────────────────────┐    │
│  │  MCP Client Integration             │    │
│  │  - Context management               │    │
│  │  - Session persistence              │    │
│  └────────────┬───────────────────────┘    │
└───────────────┼─────────────────────────────┘
                │
┌───────────────▼─────────────────────────────┐
│          MCP Server Layer                   │
│  - Protocol handling                        │
│  - Context orchestration                    │
│  - Multi-model routing                      │
└───────────────┬─────────────────────────────┘
                │
        ┌───────┴────────┐
        │                │
┌───────▼──────┐  ┌──────▼──────────┐
│  RAG Service  │  │  LLM Provider   │
│  (ChromaDB)   │  │  (Bielik)       │
│  - Cars       │  │  - HuggingFace  │
│  - Apartments │  │  - API/Local    │
└───────────────┘  └─────────────────┘
```

## Technical Recommendations

### Priority 1: Core Enhancements
1. **Implement MCP Layer**
   - Library: `modelcontextprotocol` (Python)
   - Add context persistence (SQLite table: mcp_sessions)
   - Unified enhancement endpoint

2. **Add RAG Foundation**
   - Install: ChromaDB, sentence-transformers
   - Create: /backend/services/rag_service.py
   - Seed with existing vehicle data + manual domain knowledge

3. **Refactor Domain Logic**
   - Extract car-specific code to domain handlers
   - Generic enhancement service
   - Domain configuration registry

### Priority 2: Multi-Domain Support
1. **Add Apartment Domain**
   - Model: Apartment (location, rooms, area, floor, amenities)
   - RAG: Apartment knowledge base
   - Schema: ApartmentSchema in CategorySchema

2. **Frontend Flexibility**
   - Domain selector component
   - Dynamic form generation from CategorySchema
   - Domain-specific validation

### Priority 3: Advanced Features
1. **Context Learning**
   - Store successful enhancements
   - User feedback loop
   - Fine-tune prompts per domain

2. **Multi-Model Support**
   - Bielik for Polish
   - GPT-4/Claude for comparison
   - Model selection API

3. **RAG Improvements**
   - Auto-update embeddings from new listings
   - Hybrid search (vector + keyword)
   - Domain knowledge curator interface

## Implementation Risks & Mitigations

### Risk 1: Complexity Overhead
- Current: Simple FastAPI service, works
- With MCP+RAG: Multiple services, vector DB, context management
- **Mitigation**: Incremental rollout, keep current AI as fallback

### Risk 2: Performance
- RAG queries add latency (50-200ms)
- Vector search on every request
- **Mitigation**: Cache embeddings, async processing, response streaming

### Risk 3: Resource Requirements
- ChromaDB disk space (GB for large corpus)
- Embedding computation (CPU/GPU)
- **Mitigation**: Start small, use quantized models, cloud vector DB option

### Risk 4: Multi-Domain Divergence
- Different domains = different logic everywhere
- Hard to maintain
- **Mitigation**: Strong abstraction layer, shared interfaces, plugin architecture

## Minimal Viable Implementation (MVP)

### Week 1: MCP Integration
- Install MCP libraries
- Create /backend/mcp_service.py
- Add context table
- Update /enhance-description endpoint
- Test with existing Bielik

### Week 2: Basic RAG
- Install ChromaDB
- Create /backend/services/rag_service.py
- Seed cars collection from CSV
- Integrate retrieval in enhancement flow
- A/B test with/without RAG

### Week 3: Generic Architecture
- Extract domain configs
- Create DomainHandler base class
- Refactor car-specific code
- Add domain parameter to APIs

### Week 4: Second Domain (Apartments)
- Define Apartment model
- Create apartment RAG corpus (manual)
- Add apartment routes
- Frontend domain selector

## Cost-Benefit Analysis

### Benefits
✅ Multi-domain platform (scalable to any listing type)
✅ Better descriptions via RAG context
✅ MCP enables advanced orchestration
✅ Reusable infrastructure
✅ Competitive advantage (AI-enhanced listings)

### Costs
❌ Dev time: 3-4 weeks
❌ Infrastructure: Vector DB, MCP server
❌ Maintenance: Multiple RAG collections
❌ Complexity: Higher learning curve

### Recommendation
**YES, proceed** - Architecture is flexible, existing models support it, ROI high if multi-domain is long-term goal

## Next Steps

1. **Prototype RAG** (1-2 days)
   - Install ChromaDB
   - Test car embeddings
   - Benchmark retrieval quality

2. **MCP Proof-of-Concept** (2-3 days)
   - Basic MCP server
   - Context persistence
   - Integration with Bielik

3. **Architecture Decision**
   - Single RAG vs per-domain
   - MCP server separate vs in-process
   - Domain abstraction approach

4. **Production Readiness**
   - Error handling
   - Monitoring
   - Fallback strategies
   - Documentation
