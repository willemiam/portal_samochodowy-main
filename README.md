# Portal Samochodowy

This project is a full-stack web application for managing car listings. It consists of a Svelte (Vite) frontend, a Flask backend with a SQLite database, and an optional AI enhancement microservice. All services are containerized and orchestrated using Docker Compose for easy local development.

## Features
- User registration and management
- Car listing creation, editing, and filtering with AI-enhanced descriptions
- RESTful API (Flask backend)
- Modern frontend (Svelte + Vite)
- SQLite database (auto-populated from CSV on first run)
- Optional AI description enhancement microservice (FastAPI + HuggingFace)

## Project Structure
```
portal_samochodowy-main/
│
├── backend/           # Flask backend (API, database, models)
│   ├── app.py
│   ├── routes.py
│   ├── models.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── ...
│
├── frontend/          # Svelte frontend (Vite)
│   ├── src/
│   ├── package.json
│   ├── Dockerfile
│   └── ...
│
├── docker-compose.yml # Compose file to run both services
└── README.md          # Project documentation
```

## Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows, Mac) or Docker Engine (Linux)
- (Optional) [DB Browser for SQLite](https://sqlitebrowser.org/) to inspect the database

## Quick Start (with Docker Compose)

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd portal_samochodowy-main
   ```

2. **Build and run the containers:**
   ```sh
   docker-compose up --build
   ```
   This will start both the backend (Flask) and frontend (Svelte) services.

3. **Access the application:**
   - Frontend: [http://localhost:5173](http://localhost:5173)
   - Backend API: [http://localhost:5000](http://localhost:5000)

4. **Optional AI Enhancement Service:**
   - If you have the AI microservice setup, it should run on [http://localhost:8000](http://localhost:8000)
   - The AI service enhances car descriptions automatically when adding new listings
   - Without the AI service, the application works normally but without description enhancement

5. **Database:**
   - The SQLite database (`vehicles.db`) is created automatically in the `backend` folder.
   - On first run, data is loaded from `final_vehicle_data.csv` if present.

## Development Notes
- Any changes to the code will be reflected live if you use the provided `volumes` in `docker-compose.yml`.
- If you add new Python or Node.js dependencies, update `requirements.txt` (backend) or `package.json` (frontend) and rebuild the containers.
- The AI enhancement service is optional and runs separately on port 8000 if available.

## AI Enhancement Service
The application integrates with an optional FastAPI-based AI microservice that:
- Generates enhanced marketing descriptions for car listings
- Uses HuggingFace LLM models for natural language generation
- Expects CarData schema: `{make, model, year, mileage, features[], condition}`
- Returns enhanced descriptions in Polish language
- Runs independently on port 8000 with CORS support

**Without the AI service:** The application works normally, but the "Generate Description" button will show an error message indicating the service is unavailable.

## Useful Commands
- Stop the app: `docker-compose down`
- Rebuild after changes: `docker-compose up --build`

## Troubleshooting
- Ensure Docker Desktop is running before starting the project.
- If ports 5000, 5173, or 8000 are in use, stop other services or change the ports in `docker-compose.yml`.
- For database inspection, use DB Browser for SQLite and open `backend/vehicles.db`.
- If the AI enhancement service is not working, check if it's running on port 8000 or if the service is configured properly.
- The application will work without the AI service, but description generation will not be available.

---

**Enjoy using Portal Samochodowy!**
