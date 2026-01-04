import os

path = "."

class Preferences:
    def __init__(self):
        self.setupwebbackend: bool = True
        self.exposebackend: bool = False
        self.backendport: int = 5000
        self.frontend: bool = True
        self.port: int = 80
        self.db: bool = True
        self.pocketbaseport: int = 8080
        self.htmx: bool = True

preferences = Preferences()
def setup_folders(preferences: Preferences):
    if preferences.frontend:
        os.makedirs(path + "/frontend")
        os.makedirs(path + "/frontend/components")
        os.makedirs(path + "/frontend/js")
        os.makedirs(path + "/frontend/css")

    os.makedirs(path + "/backend")
    os.makedirs(path + "/extras")
    os.system("git init")
    os.system(f"cd {path}/backend && uv init && uv sync")
    if preferences.setupwebbackend:
        os.system(f"cd {path}/backend && uv add pocketbase && uv add fastapi && uv add uvicorn")
def setup_backend(preferences: Preferences):
    open(path + "/backend/main.py", "w").write(f"""from fastapi import FastAPI
import pocketbase
pb = pocketbase.PocketBase("http://pocketbase:{preferences.pocketbaseport}")
app = FastAPI()
@app.get("/")
def root():
    return "Hello World"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
    """)
def setup_frontend(preferences: Preferences):
    frontendboilerplate = """
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="ie=edge">
        <title>HTML 5 Boilerplate</title>
        """
    if preferences.htmx:
        frontendboilerplate += """
        <script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.8/dist/htmx.js" integrity="sha384-ezjq8118wdwdRMj+nX4bevEi+cDLTbhLAeFF688VK8tPDGeLUe0WoY2MZtSla72F" crossorigin="anonymous"></script>"""
    if preferences.setupwebbackend:
        frontendboilerplate += """
        <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>"""
        frontendboilerplate += """
        <link href="https://cdn.jsdelivr.net/npm/daisyui@5" rel="stylesheet" type="text/css" />
        <!-- <link rel="stylesheet" href="style.css"> -->
      </head>
      <body>
        <!-- <script src="index.js"></script> -->
      </body>
    </html>
    """
    open(path + "/frontend/index.php", "w").write(frontendboilerplate)
    
def dockerconfig(preferences: Preferences):
    config = """services:"""
    if preferences.frontend:
        config += f"""
      php_app:
        image: php:8.3-fpm
        volumes:
          - ./frontend:/var/www/html

      nginx_server:
        image: nginx:alpine
        ports:
          - "{preferences.port}:80" # change the first port number to match your needs
        volumes:
          - ./frontend:/var/www/html
          - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      """
    config += """
      backend:
        build: ./backend
        command: uv run main.py
        restart: always""" 
    if preferences.exposebackend:
        config += f"""
        ports:
          - "{preferences.backendport}:5000""" 
      
    if preferences.db:
      config += f"""
      pocketbase:
        image: ghcr.io/muchobien/pocketbase:latest
        ports:
          - "{preferences.pocketbaseport}:8080"
        volumes:
          - ./pb_data:/pb_data
        command:
          - serve
          - --http=0.0.0.0:8080
          - --dir=/pb_data
        restart: unless-stopped"""
    composefile = open(path + "/docker-compose.yml", "w")
    composefile.write(config)
    composefile.close()
    serverconfig = """FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_DEV=1

# Optimized layer caching
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY . .
RUN uv sync --frozen --no-dev

CMD ["uv", "run", "main.py"]"""
    dockerfile = open(path + "/backend/Dockerfile", "w")
    dockerfile.write(serverconfig)
    dockerfile.close()

    nginxconfig = """server {
        listen 80;
        root /var/www/html;

        # Use Docker's internal DNS resolver
        resolver 127.0.0.11 valid=30s;

        location / {
            index index.php;
            try_files $uri $uri/ /index.php?$query_string;
        }

        location ~ \.php$ {
            # Using a variable prevents Nginx from crashing if php_app is down
            set $upstream php_app:9000;
            fastcgi_pass $upstream;
            include fastcgi_params;
            fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        }
    }"""

    nginxfile = open(path + "/nginx.conf", "w")
    nginxfile.write(nginxconfig)
    nginxfile.close()

def setup() -> Preferences:
    preferences = Preferences()
    print("==============================================\nWelcome to JayStack!")
    preferences.frontend = input("Setup frontend? (y/n): ") == "y"
    if preferences.frontend:
        preferences.port = int(input("Frontend port: "))
        preferences.htmx = input("Setup htmx? (y/n): ") == "y"
    
    if preferences.setupwebbackend:
        preferences.setupwebbackend = input("Setup web backend? (y/n): ") == "y"
        preferences.exposebackend = input("Expose backend? (y/n): ") == "y"
        if preferences.exposebackend:
            preferences.backendport = int(input("Public backend port: "))
    preferences.db = input("Setup database? (y/n): ") == "y"
    if preferences.db:
        preferences.pocketbaseport = int(input("Public pocketbase port: "))
    return preferences
if __name__ == "__main__":
    preferences = setup()
    setup_folders(preferences)
    dockerconfig(preferences)
    if preferences.frontend:
        setup_frontend(preferences)
    if preferences.setupwebbackend:
        setup_backend(preferences)
    print(f"""Your project is ready!\n
    start it with: sudo docker compose up -d\n
    If you have a frontend you can acces it at http://localhost:{preferences.port}
    If you have a backend you can acces it at http://localhost:{preferences.backendport} publicly and http://backend:5000 privately
    If you have a database you can acces it at http://localhost:{preferences.pocketbaseport}/_ (enter sudo docker logs pocketbase to get the password) 
    and http://pocketbase:8080 privately
    """)