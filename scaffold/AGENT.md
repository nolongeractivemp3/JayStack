# Tech Stack

This project is split into a frontend and backend folder.
The frontend uses PHP for data and HTMX for loading components (simple PHP files you can write in /frontend/components). It also has DaisyUI with Tailwind CSS for styling.
The backend uses Python, Uvicorn for the server, and FastAPI for the API.
You can disable backend if it is not needed by removing it from docker-compose.yml.
We use PocketBase for the database.

# Commands

docker compose up -d --build
docker compose logs
docker compose down
