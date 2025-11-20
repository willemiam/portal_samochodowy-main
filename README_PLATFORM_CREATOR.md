# Platform Creator - Setup and Usage Guide

This guide explains how to run and test the Platform Creator wizard skeleton locally.

## Overview

The Platform Creator is a multi-step wizard that allows users to configure and create new platforms. It consists of:

- **Frontend**: Svelte-based wizard with 5 steps (Basic Info, Features, Domain Details, Advanced, Summary)
- **Backend**: Flask API with file-based JSON storage providing platform creation and preview endpoints

## Prerequisites

- Python 3.7+ (for backend)
- Node.js 14+ and npm (for frontend)

## Backend Setup

### 1. Install Dependencies

```bash
cd backend
pip install Flask flask-cors
```

All required dependencies are:
- Flask
- flask-cors

### 2. Run the Backend

```bash
cd backend
python app.py
```

The backend will start on `http://localhost:5000`

### 3. Verify Backend is Running

Test the health of the server:

```bash
curl http://localhost:5000/api/items
```

You should see a JSON response (may be empty initially).

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Run the Frontend

```bash
cd frontend
npm run dev
```

The frontend will start on `http://localhost:5173` (or another port shown in the terminal).

### 3. Access the Platform Creator

Open your browser and navigate to:
```
http://localhost:5173/platform-creator
```

## API Endpoints

### POST /api/platforms

Create a new platform.

**Request:**
```bash
curl -X POST http://localhost:5000/api/platforms \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Automotive Platform",
    "description": "A platform for automotive enthusiasts",
    "domain": "automotive",
    "features": ["search", "filters", "comparison"],
    "targetAudience": "Car buyers and dealers",
    "primaryGoals": ["Increase user engagement", "Improve conversion rates"],
    "customSettings": {
      "max_results": "100",
      "cache_enabled": "true"
    }
  }'
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-11-20T14:30:00.000000"
}
```

### GET /api/platforms/{id}

Retrieve a specific platform by ID.

**Request:**
```bash
curl http://localhost:5000/api/platforms/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "data": {
    "name": "My Automotive Platform",
    "description": "A platform for automotive enthusiasts",
    "domain": "automotive",
    "features": ["search", "filters", "comparison"],
    "targetAudience": "Car buyers and dealers",
    "primaryGoals": ["Increase user engagement", "Improve conversion rates"],
    "customSettings": {
      "max_results": "100",
      "cache_enabled": "true"
    }
  },
  "previews": [],
  "created_at": "2025-11-20T14:30:00.000000"
}
```

### POST /api/platforms/{id}/preview

Generate a preview for a platform.

**Request:**
```bash
curl -X POST http://localhost:5000/api/platforms/550e8400-e29b-41d4-a716-446655440000/preview \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "platform_id": "550e8400-e29b-41d4-a716-446655440000",
  "enhanced_text": "# Platform Preview: My Automotive Platform\n\n## Overview\nThis is a mock preview for the My Automotive Platform platform in the automotive domain.\n\n## Features\nThe platform has been configured with the following capabilities:\n- Enhanced AI processing\n- Real-time data analysis\n- Custom domain integration\n\n## Status\nPreview generated successfully. This is a placeholder for actual AI-enhanced content.",
  "sources": [],
  "session_id": "770e8400-e29b-41d4-a716-446655440002",
  "created_at": "2025-11-20T14:35:00.000000"
}
```

## End-to-End Testing

### Manual Testing Flow

1. **Start the backend** (see Backend Setup above)
2. **Start the frontend** (see Frontend Setup above)
3. **Navigate to the wizard**: http://localhost:5173/platform-creator
4. **Complete the wizard steps**:
   - Step 1 (Basic Info): Enter name, description, and domain
   - Step 2 (Features): Select desired features
   - Step 3 (Domain Details): Describe target audience and goals
   - Step 4 (Advanced): Add custom settings (optional)
   - Step 5 (Summary): Review and save
5. **Click "Save Platform"**: Should see success message with platform ID
6. **Click "Generate Preview"**: Should see enhanced preview text displayed
7. **Verify data persistence**: Check `backend/data/platforms.json` for saved data

### Test with Backend Offline

The frontend is designed to handle errors gracefully. If the backend is not running:

1. Navigate to: http://localhost:5173/platform-creator
2. Complete the wizard steps
3. Click "Save Platform"
4. You should see an error message (not a crash)
5. The wizard should remain functional

## File Structure

```
portal_samochodowy-main/
├── backend/
│   ├── app.py                      # Flask app with blueprint registration
│   ├── services/
│   │   └── platforms.py            # Platform API blueprint
│   └── data/
│       └── platforms.json          # File-based storage (created automatically)
├── frontend/
│   └── src/
│       ├── App.svelte              # Main app (updated with /platform-creator route)
│       ├── routes/
│       │   └── platformCreator.svelte
│       └── lib/
│           ├── api/
│           │   └── platform.ts     # API helper functions
│           ├── stores/
│           │   └── wizardStore.ts  # Wizard state management
│           └── components/
│               ├── CreatorWizard.svelte
│               ├── StepBasicInfo.svelte
│               ├── StepFeatures.svelte
│               ├── StepDomainDetails.svelte
│               ├── StepAdvanced.svelte
│               └── StepSummary.svelte
└── README_PLATFORM_CREATOR.md      # This file
```

## Acceptance Criteria

✅ **Frontend pages render the wizard without runtime errors**
- Navigate to /platform-creator
- All 5 steps should be visible and functional
- Progress bar should update when navigating between steps

✅ **Backend runs and exposes endpoints**
- `python backend/app.py` starts server on port 5000
- POST /api/platforms creates and returns platform ID
- GET /api/platforms/{id} retrieves platform data
- POST /api/platforms/{id}/preview returns mock preview with enhanced_text

✅ **E2E manual flow works**
- Save button POSTs to /api/platforms and displays returned ID
- Preview button calls POST /api/platforms/{id}/preview
- Enhanced text is displayed in the UI
- Data is persisted in backend/data/platforms.json

✅ **Error handling**
- Frontend displays error messages when backend is unavailable
- Frontend does not crash or break when API calls fail

## Storage Format

Platforms are stored in `backend/data/platforms.json` with the following structure:

```json
{
  "550e8400-e29b-41d4-a716-446655440000": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "data": {
      "name": "My Platform",
      "description": "...",
      "domain": "automotive",
      "features": [...],
      "targetAudience": "...",
      "primaryGoals": [...],
      "customSettings": {...}
    },
    "previews": [
      {
        "id": "preview-uuid",
        "platform_id": "platform-uuid",
        "enhanced_text": "...",
        "sources": [],
        "session_id": "session-uuid",
        "created_at": "..."
      }
    ],
    "created_at": "2025-11-20T14:30:00.000000"
  }
}
```

## Troubleshooting

### Backend won't start
- Ensure Flask and flask-cors are installed: `pip install Flask flask-cors`
- Check port 5000 is not already in use
- Check Python version: `python --version` (should be 3.7+)

### Frontend won't start
- Run `npm install` in the frontend directory
- Check Node.js version: `node --version` (should be 14+)
- Clear node_modules and reinstall if needed

### CORS errors
- Ensure backend is running and CORS is enabled (it should be by default in app.py)
- Check that frontend is making requests to http://localhost:5000

### 404 errors on /platform-creator route
- Ensure App.svelte has been updated with the new route
- Restart the frontend dev server: `npm run dev`

## Next Steps

This is a skeleton implementation. Future enhancements could include:

- Real AI integration for preview generation
- User authentication integration
- Database storage instead of file-based JSON
- Platform editing and deletion
- Advanced validation and error handling
- Platform deployment capabilities
- Analytics and monitoring
