# Platform Creator - Setup and Usage Guide

This document provides instructions for running and testing the Platform Creator feature, which allows users to create custom platforms through a wizard interface.

## Overview

The Platform Creator consists of:
- **Frontend**: Svelte-based wizard with 5 steps (Basic Info, Features, Domain Details, Advanced, Summary)
- **Backend**: Flask API with endpoints for creating platforms and generating previews using mock MCP

## Architecture

```
Frontend (Svelte)                    Backend (Flask)
├── CreatorWizard.svelte            ├── services/platforms.py
├── StepBasicInfo.svelte            │   ├── POST /api/platforms
├── StepFeatures.svelte             │   ├── GET /api/platforms/{id}
├── StepDomainDetails.svelte        │   └── POST /api/platforms/{id}/preview
├── StepAdvanced.svelte             └── data/platforms.json (storage)
├── StepSummary.svelte
├── stores/wizardStore.ts
└── api/platform.ts
```

## Prerequisites

- **Node.js** (v16+) and npm
- **Python** (3.8+)
- **pip** (Python package manager)

## Installation

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure the data directory exists:
   ```bash
   mkdir -p data
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install npm dependencies:
   ```bash
   npm install
   ```

## Running the Application

### Start Backend (Flask)

In the `backend` directory:

```bash
python app.py
```

The backend will start on **http://localhost:5000**

You should see output like:
```
 * Running on http://0.0.0.0:5000
 * Restarting with stat
```

### Start Frontend (Svelte)

In the `frontend` directory:

```bash
npm run dev
```

The frontend will start on **http://localhost:5173**

You should see output like:
```
  VITE v6.0.11  ready in XXX ms

  ➜  Local:   http://localhost:5173/
```

## Usage

### Accessing the Platform Creator

1. Open your browser and navigate to: **http://localhost:5173**
2. You'll see the Platform Creator Wizard

### Creating a Platform

Follow these steps in the wizard:

#### Step 1: Basic Information
- **Platform Name**: Enter a name for your platform (e.g., "Car Marketplace")
- **Description**: Optional description
- **Domain**: The category of items (e.g., "automotive", "real-estate")

#### Step 2: Features
Select features to enable:
- ✅ Search
- ✅ Advanced Filters
- ✅ AI Enhancement (via MCP)
- ✅ User Accounts

#### Step 3: Domain Details
- **Item Name (Singular)**: What you call one item (e.g., "Car")
- **Item Name (Plural)**: Plural form (e.g., "Cars")
- **Primary Fields**: Key attributes (e.g., "make", "model", "year")

#### Step 4: Advanced Settings (Optional)
- **MCP Endpoint**: URL for Model Context Protocol service
- **API Key**: Authentication key
- **Custom Prompt**: Template for AI enhancement

#### Step 5: Summary
- Review your configuration
- Click **"Save Platform"** to create it
- Use **"Generate Preview"** to test AI enhancement

### Testing Preview Functionality

After saving a platform:

1. Stay on the Summary step
2. Click **"Generate Preview"**
3. You'll see a mock AI-enhanced description based on your domain and sample data
4. The preview demonstrates how MCP would enhance item descriptions

## API Reference

### POST /api/platforms

Create a new platform configuration.

**Request:**
```bash
curl -X POST http://localhost:5000/api/platforms \
  -H "Content-Type: application/json" \
  -d '{
    "platform_config": {
      "name": "Car Marketplace",
      "description": "A platform for buying and selling cars",
      "domain": "automotive",
      "features": {
        "search": true,
        "filters": true,
        "aiEnhancement": true,
        "userAccounts": false
      },
      "domainDetails": {
        "itemName": "Car",
        "itemNamePlural": "Cars",
        "primaryFields": ["make", "model", "year"]
      },
      "advanced": {
        "mcpEndpoint": "",
        "apiKey": "",
        "customPrompt": ""
      }
    }
  }'
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "Platform created successfully",
  "platform_config": { ... }
}
```

### GET /api/platforms/{id}

Retrieve a platform configuration by ID.

**Request:**
```bash
curl http://localhost:5000/api/platforms/123e4567-e89b-12d3-a456-426614174000
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "platform_config": { ... },
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "previews": []
}
```

### POST /api/platforms/{id}/preview

Generate a preview using mock MCP.

**Request:**
```bash
curl -X POST http://localhost:5000/api/platforms/123e4567-e89b-12d3-a456-426614174000/preview \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "automotive",
    "item_data": {
      "make": "Toyota",
      "model": "Camry",
      "year": "2023",
      "color": "Blue"
    }
  }'
```

**Response:**
```json
{
  "id": "preview-uuid",
  "enhanced_text": "[MOCK MCP RESPONSE] Enhanced description for automotive item. Item details: make: Toyota, model: Camry, year: 2023, color: Blue. This is a simulated AI-enhanced description...",
  "sources": [],
  "session_id": "session-uuid",
  "created_at": "2024-01-15T10:35:00"
}
```

## Data Storage

Platform configurations are stored in:
```
backend/data/platforms.json
```

This is a simple JSON file-based storage. Each platform entry includes:
- Platform configuration
- Creation and update timestamps
- Preview history

## Error Handling

### Backend Not Running
If the backend is not running, the frontend will:
- Display errors when trying to save or preview
- Show user-friendly error messages
- Allow continued navigation through wizard steps

### Frontend Error Messages
- "Platform must be saved before preview" - Save platform first
- "Failed to create platform" - Check backend connectivity
- "Failed to generate preview" - Verify platform ID and backend status

## Development Notes

### Mock MCP
The preview endpoint uses a **mock MCP implementation** that:
- Generates simulated AI-enhanced descriptions
- Returns placeholder data for sources and session IDs
- Demonstrates the expected interface for real MCP integration

### Future Enhancements
To integrate with a real MCP service:
1. Update `backend/services/platforms.py`
2. Replace mock response with actual MCP API calls
3. Use platform's `advanced.mcpEndpoint` and `advanced.apiKey`
4. Implement proper error handling and retries

## Troubleshooting

### Port Already in Use
If port 5000 or 5173 is in use:

**Backend:**
```bash
# Change port in app.py
python app.py  # Edit line: app.run(debug=True, host='0.0.0.0', port=5001)
```

**Frontend:**
```bash
# Change port in vite.config.js or use:
npm run dev -- --port 5174
```

### CORS Issues
If you encounter CORS errors:
- Verify CORS is enabled in `backend/app.py`
- Check that frontend URL is correct in API calls
- Ensure backend is running before making frontend requests

### Platform Not Saving
- Check browser console for errors
- Verify backend logs for error messages
- Ensure `backend/data/` directory is writable

## Acceptance Criteria

✅ **Frontend renders wizard without errors**
- Navigate through all 5 steps
- Form validation works correctly
- UI is responsive and functional

✅ **Backend exposes required endpoints**
- POST /api/platforms creates platforms
- GET /api/platforms/{id} retrieves platforms
- POST /api/platforms/{id}/preview generates mock previews

✅ **E2E Manual Test**
- Create a platform via wizard → Returns platform ID
- Use Preview button → Displays mock enhanced text
- Data persists in platforms.json

## Support

For issues or questions, refer to the main project README.md or create an issue in the repository.
