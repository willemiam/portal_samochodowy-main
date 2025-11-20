# Platform Creator Wizard - Documentation

## Overview

This feature adds a complete platform creator wizard that allows users to configure and preview custom platforms. It includes a multi-step frontend wizard built with Svelte and a Flask backend with mock MCP (Model Context Protocol) preview functionality.

## Architecture

### Frontend Components

- **CreatorWizard.svelte**: Main wizard container with step navigation
- **StepBasicInfo.svelte**: Collects platform name, description, and domain
- **StepFeatures.svelte**: Feature selection with checkboxes
- **StepDomainDetails.svelte**: Domain-specific configuration (placeholder)
- **StepAdvanced.svelte**: Advanced settings (theme, language, etc.)
- **StepSummary.svelte**: Configuration review and preview testing
- **wizardStore.ts**: Centralized state management using Svelte stores
- **platform.ts**: API client for backend communication

### Backend Components

- **services/platforms.py**: Platform management service with JSON storage
- **routes.py**: Three new API endpoints for platform CRUD and preview
- **data/platforms.json**: Persistent JSON storage for platform configurations

## API Endpoints

### 1. Create Platform
```bash
POST /api/platforms
Content-Type: application/json

{
  "config": {
    "name": "My Platform",
    "description": "Platform description",
    "domain": "automotive",
    "features": ["search", "ai-descriptions"],
    "domainDetails": {},
    "advanced": {
      "theme": "light",
      "language": "en"
    }
  }
}

Response: 201 Created
{
  "id": "uuid-string",
  "config": { ... },
  "created_at": "2025-11-20T15:00:00.000000"
}
```

### 2. Get Platform
```bash
GET /api/platforms/{platform_id}

Response: 200 OK
{
  "id": "uuid-string",
  "config": { ... },
  "created_at": "2025-11-20T15:00:00.000000"
}
```

### 3. Generate Preview
```bash
POST /api/platforms/{platform_id}/preview
Content-Type: application/json

{
  "domain": "automotive",
  "item_data": {
    "name": "Toyota Camry 2023",
    "make": "Toyota",
    "model": "Camry",
    "year": 2023,
    "price": 25000
  }
}

Response: 200 OK
{
  "enhanced_text": "[MOCK ENHANCED] Toyota Camry 2023 — make: Toyota ...",
  "sources": [],
  "session_id": "uuid-string",
  "timestamp": "2025-11-20T15:00:00.000000"
}
```

## Running Locally

### Prerequisites

- Python 3.8+ with pip
- Node.js 16+ with npm
- Git

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the Flask development server
python app.py
```

The backend will start on `http://localhost:5000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the Vite development server
npm run dev
```

The frontend will start on `http://localhost:5173`

### Access the Wizard

Open your browser and navigate to:
```
http://localhost:5173/creator
```

## Manual Testing Guide

### Test 1: Create and Save Platform

1. Navigate to `http://localhost:5173/creator`
2. Fill in Step 1 (Basic Info):
   - Platform Name: "Automotive Sales Platform"
   - Description: "A comprehensive platform for buying and selling vehicles"
   - Domain: "automotive"
3. Click step 2 or "Next" to go to Features
4. Select features: "Advanced Search", "AI-Enhanced Descriptions", "Image Upload"
5. Navigate through Domain Details and Advanced steps (optional)
6. Go to Summary step
7. Click "Save Platform"
8. Verify success message with platform ID

### Test 2: Generate Preview

1. After saving (Test 1), the preview section appears
2. Modify the sample JSON data or keep default:
   ```json
   {
     "name": "Sample Car",
     "make": "Toyota",
     "model": "Camry",
     "year": 2023,
     "price": 25000
   }
   ```
3. Click "Generate Preview"
4. Verify enhanced text appears showing mock MCP output

### Test 3: cURL Commands

Create a platform:
```bash
curl -X POST http://localhost:5000/api/platforms \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "name": "Test Platform",
      "description": "Testing via cURL",
      "domain": "automotive",
      "features": ["search"],
      "domainDetails": {},
      "advanced": {"theme": "light", "language": "en"}
    }
  }'
```

Get a platform (replace {id} with actual ID):
```bash
curl http://localhost:5000/api/platforms/{id}
```

Generate preview:
```bash
curl -X POST http://localhost:5000/api/platforms/{id}/preview \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "automotive",
    "item_data": {
      "name": "Honda Civic",
      "make": "Honda",
      "model": "Civic",
      "year": 2024,
      "price": 30000
    }
  }'
```

## Features Implemented

✅ Multi-step wizard with navigation  
✅ Form validation (basic info required)  
✅ State management with Svelte stores  
✅ Feature selection UI  
✅ Configuration summary display  
✅ Platform save functionality  
✅ Mock MCP preview generation  
✅ JSON-based persistent storage  
✅ Error handling for API calls  
✅ Responsive design  
✅ CORS enabled for local development  

## Future Enhancements

This is a skeleton implementation. Future PRs will add:

- Real MCP integration (replacing mock)
- ChromaDB integration for context storage
- LLM integration for enhanced descriptions
- Dynamic domain-specific field generation
- User authentication for platform management
- Platform editing and deletion
- Template system for common domains
- Export/import platform configurations

## Technical Notes

### Storage

Platform configurations are stored in `/backend/data/platforms.json`. This file is created automatically on first use. Each platform entry includes:
- Unique UUID
- Full configuration object
- Creation timestamp
- Array of preview history

### State Management

The wizard uses Svelte's writable stores for reactive state management. The store updates on blur events to ensure data persistence as users navigate between steps.

### Error Handling

- Frontend handles API errors gracefully with user-friendly messages
- Backend returns appropriate HTTP status codes
- Invalid JSON in form fields shows console warnings but doesn't break the app

## Screenshots

### Step 1: Basic Information
![Wizard Step 1](https://github.com/user-attachments/assets/f460385b-3815-4374-a657-9553c8ad06d6)

### Step 5: Summary with Preview
![Wizard Summary with Preview](https://github.com/user-attachments/assets/71df1ddc-b55b-4429-8884-f7c3d8f79805)

## Support

For issues or questions, please refer to the main repository README or open an issue on GitHub.
