import os
import zipfile
import uuid
from git import Repo, GitCommandError

# ==============================
# Configuration
# ==============================

SUPPORTED_EXTENSIONS = (
    ".py", ".js", ".ts", ".tsx",
    ".java", ".cpp", ".c",
    ".go", ".rs"
)


EXCLUDED_DIRS = {
    "node_modules",
    ".git",
    "venv",
    "__pycache__",
    "dist",
    "build",
    ".next",
    ".idea"
}

MAX_FILE_SIZE_MB = 1  # Skip files larger than 1MB
BASE_UPLOAD_DIR = "uploads"

os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)

# ==============================
# ZIP Upload Handling
# ==============================

def save_zip_file(upload_file):
    project_id = str(uuid.uuid4())
    project_path = os.path.join(BASE_UPLOAD_DIR, project_id)
    os.makedirs(project_path, exist_ok=True)

    zip_path = os.path.join(project_path, "repo.zip")

    try:
        # Save uploaded ZIP
        with open(zip_path, "wb") as buffer:
            buffer.write(upload_file.file.read())

        # Extract ZIP safely
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(project_path)

    except zipfile.BadZipFile:
        raise ValueError("Invalid ZIP file uploaded.")

    finally:
        # Optional: remove zip after extraction
        if os.path.exists(zip_path):
            os.remove(zip_path)

    return project_id, project_path


# ==============================
# GitHub Clone Handling
# ==============================

def clone_github_repo(repo_url):
    project_id = str(uuid.uuid4())
    project_path = os.path.join(BASE_UPLOAD_DIR, project_id)

    try:
        Repo.clone_from(repo_url, project_path)
    except GitCommandError as e:
        raise ValueError(f"Failed to clone repository: {str(e)}")

    return project_id, project_path


# ==============================
# Code File Extraction
# ==============================

def get_code_files(project_path):
    code_files = []

    for root, dirs, files in os.walk(project_path):

        # Remove excluded directories (in-place modification)
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in files:

            # Skip hidden files
            if file.startswith("."):
                continue

            # Case-insensitive extension match
            if not file.lower().endswith(SUPPORTED_EXTENSIONS):
                continue

            full_path = os.path.join(root, file)

            try:
                # Skip large files
                size_mb = os.path.getsize(full_path) / (1024 * 1024)
                if size_mb > MAX_FILE_SIZE_MB:
                    continue

                code_files.append(full_path)

            except OSError:
                # Skip unreadable files safely
                continue

    return code_files
