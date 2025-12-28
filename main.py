import os

path = "."


def setup_folders():
    os.makedirs(path + "/frontend")
    os.makedirs(path + "/frontend/components")
    os.makedirs(path + "/frontend/js")
    os.makedirs(path + "/frontend/css")

    os.makedirs(path + "/backend")
    os.makedirs(path + "/extras")
    os.system("git init")
    os.system(f"cd {path}/backend && uv init && uv sync")

    frontendboilerplate = """
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="ie=edge">
        <title>HTML 5 Boilerplate</title>
        <link href="https://cdn.jsdelivr.net/npm/daisyui@5" rel="stylesheet" type="text/css" />
        <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
        <script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.8/dist/htmx.js" integrity="sha384-ezjq8118wdwdRMj+nX4bevEi+cDLTbhLAeFF688VK8tPDGeLUe0WoY2MZtSla72F" crossorigin="anonymous"></script>
        <!-- <link rel="stylesheet" href="style.css"> -->
      </head>
      <body>
        <!-- <script src="index.js"></script> -->
      </body>
    </html>
    """
    open(path + "/frontend/index.php", "w").write(frontendboilerplate)


def dockerconfig():
    config = """services:
      php_app:
        image: php:8.3-fpm
        volumes:
          - ./frontend:/var/www/html

      nginx_server:
        image: nginx:alpine
        ports:
          - "80:80" # change the first port number to match your needs
        volumes:
          - ./frontend:/var/www/html
          - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      backend:
        build: ./backend
        command: uv run main.py
        restart: always
      pocketbase:
        image: ghcr.io/muchobien/pocketbase:latest
        ports:
          - "8080:8080"
        volumes:
          - ./pb_data:/pb_data
        command:
          - serve
          - --http=0.0.0.0:8080
          - --dir=/pb_data
        restart: unless-stopped

    """
    composefile = open(path + "/docker-compose.yml", "w")
    composefile.write(config)
    composefile.close()
    serverconfig = """FROM python:3.12-slim
    COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvbin/uv

    # Add uv to the system PATH
    ENV PATH="/uvbin:${PATH}"

    WORKDIR /app
    COPY . .

    # Install deps if you have the files, otherwise skip
    RUN if [ -f pyproject.toml ]; then uv sync --frozen; fi

    CMD ["uv", "run", "python", "main.py"]
    """
    dockerfile = open(path + "/backend/Dockerfile", "w")
    dockerfile.write(serverconfig)
    dockerfile.close()

    nginxconfig = """server {
        listen 80;
        root /var/www/html;
        index index.php;
        location / {
            try_files $uri $uri/ /index.php?$query_string;
        }
        location ~ \.php$ {
            fastcgi_pass php_app:9000;
            include fastcgi_params;
            fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        }
    }
"""

    nginxfile = open(path + "/nginx.conf", "w")
    nginxfile.write(nginxconfig)
    nginxfile.close()


if __name__ == "__main__":
    setup_folders()
    dockerconfig()
