import os
import subprocess
import sys
import urllib.error
import urllib.request

REQUEST_TIMEOUT = 20
SOURCE_BASE_URL = "tech.jaypo.ch"
TARGET_DIR_NAME = "jaystack"

DIRECTORIES = (
    "frontend",
    "frontend/components",
    "frontend/js",
    "frontend/css",
    "backend",
    "extras",
)

SCAFFOLD_FILES = (
    "frontend/index.php",
    "backend/main.py",
    "backend/Dockerfile",
    "docker-compose.yml",
    "nginx.conf",
    "AGENT.md",
)


def run_checked(command, cwd):
    subprocess.run(command, cwd=cwd, check=True)


def create_directories(project_root):
    for relative_dir in DIRECTORIES:
        os.makedirs(os.path.join(project_root, relative_dir), exist_ok=True)


def download_file(url):
    with urllib.request.urlopen(url, timeout=REQUEST_TIMEOUT) as response:
        return response.read()


def download_scaffold_files(project_root, base_url):
    for relative_path in SCAFFOLD_FILES:
        source_url = f"{base_url}/scaffold/{relative_path}"
        destination = os.path.join(project_root, relative_path)
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        try:
            content = download_file(source_url)
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Failed to download {source_url}: {exc}") from exc
        with open(destination, "wb") as f:
            f.write(content)


def initialize_git(project_root):
    if not os.path.isdir(os.path.join(project_root, ".git")):
        run_checked(["git", "init"], cwd=project_root)


def initialize_backend(project_root):
    backend_dir = os.path.join(project_root, "backend")

    try:
        run_checked(["uv", "--version"], cwd=project_root)
    except FileNotFoundError as exc:
        raise RuntimeError("'uv' is required but was not found in PATH.") from exc

    if not os.path.isfile(os.path.join(backend_dir, "pyproject.toml")):
        run_checked(["uv", "init"], cwd=backend_dir)

    run_checked(["uv", "sync"], cwd=backend_dir)
    run_checked(["uv", "add", "pocketbase", "fastapi", "uvicorn"], cwd=backend_dir)


def main():
    base_url = SOURCE_BASE_URL.rstrip("/")
    if not base_url.startswith("http://") and not base_url.startswith("https://"):
        raise RuntimeError(
            "SOURCE_BASE_URL must start with http:// or https:// "
            f"(current: {SOURCE_BASE_URL!r})."
        )

    project_root = os.path.abspath(TARGET_DIR_NAME)

    print("==============================================")
    print("Welcome to JayStack!")
    print(f"Target directory: {project_root}")
    print(f"Scaffold source: {base_url}/scaffold/")

    create_directories(project_root)
    download_scaffold_files(project_root, base_url)
    initialize_git(project_root)
    initialize_backend(project_root)

    print(
        """Your project is ready!
start it with: docker compose up -d --build
Frontend: http://localhost:80
Backend (public): http://localhost:5000
Backend (internal): http://backend:5000
PocketBase (public): http://localhost:8080/_
PocketBase (internal): http://pocketbase:8080
"""
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
