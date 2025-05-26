# Portal Samochodowy

This project is a full-stack web application for managing car listings. It consists of a Svelte (Vite) frontend and a Flask backend with a SQLite database. Both services are containerized and orchestrated using Docker Compose for easy local development.

## Features
- User registration and management
- Car listing creation, editing, and filtering
- RESTful API (Flask backend)
- Modern frontend (Svelte + Vite)
- SQLite database (auto-populated from CSV on first run)

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

4. **Database:**
   - The SQLite database (`vehicles.db`) is created automatically in the `backend` folder.
   - On first run, data is loaded from `final_vehicle_data.csv` if present.

## Development Notes
- Any changes to the code will be reflected live if you use the provided `volumes` in `docker-compose.yml`.
- If you add new Python or Node.js dependencies, update `requirements.txt` (backend) or `package.json` (frontend) and rebuild the containers.

## Useful Commands
- Stop the app: `docker-compose down`
- Rebuild after changes: `docker-compose up --build`

## Troubleshooting
- Ensure Docker Desktop is running before starting the project.
- If ports 5000 or 5173 are in use, stop other services or change the ports in `docker-compose.yml`.
- For database inspection, use DB Browser for SQLite and open `backend/vehicles.db`.

---

**Enjoy using Portal Samochodowy!**
