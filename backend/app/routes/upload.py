from fastapi import APIRouter, UploadFile, File, Form
from app.services.file_service import (
    save_zip_file,
    clone_github_repo,
    get_code_files
)
from app.services.chunks_service import chunk_text
from app.services.embed_service import (
    embed_and_store,
    reset_project_embeddings
)
from app.config import settings

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/")
async def upload_repo(
    file: UploadFile = File(None),
    github_url: str = Form(None)
):
    # Fix Swagger empty file issue
    if file and file.filename == "":
        file = None

    if not file and not github_url:
        return {"error": "Provide either ZIP file or GitHub URL"}

    # Step 1: Save ZIP or Clone GitHub
    if file:
        project_id, project_path = save_zip_file(file)
    else:
        project_id, project_path = clone_github_repo(github_url)

    # Step 2: Get filtered code files
    code_files = get_code_files(project_path)

    all_chunks = []

    # Step 3: Read files + chunk
    for file_path in code_files:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
                chunks = chunk_text(text, file_path)
                all_chunks.extend(chunks)
        except Exception:
            continue  # Skip problematic files safely

    # Step 4: Embedding (only if OpenAI enabled)
    if settings.USE_OPENAI and all_chunks:
        # Clear old vectors for this project
        reset_project_embeddings(project_id)

        # Store new embeddings
        embed_and_store(all_chunks, project_id)

    return {
        "project_id": project_id,
        "total_code_files": len(code_files),
        "total_chunks": len(all_chunks),
        "embedding_mode": "openai" if settings.USE_OPENAI else "local"
    }
