import chromadb
from openai import OpenAI
from app.config import settings

# ==============================
# Chroma Setup
# ==============================

import os

chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection(
    name="codebase"
)


def reset_project_embeddings(project_id):
    collection.delete(where={"project_id": project_id})


# ==============================
# Embedding + Store
# ==============================

def embed_and_store(chunks, project_id):

    # Create OpenAI client safely
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set in .env file.")

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    for i, chunk in enumerate(chunks):

        response = client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=chunk["content"]
        )

        embedding_vector = response.data[0].embedding

        collection.add(
            documents=[chunk["content"]],
            embeddings=[embedding_vector],
            metadatas=[{
                "file_path": chunk["file_path"],
                "project_id": project_id,
                "start_line": chunk.get("start_line"),
        "end_line": chunk.get("end_line")
            }],
            ids=[f"{project_id}_{i}"]
        )


