from app.config import settings
from openai import OpenAI
import chromadb
import os

chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection("codebase")

TOP_K = 20

SUPPORTED_EXTENSIONS = (
    ".py", ".js", ".ts", ".tsx",
    ".java", ".cpp", ".c", ".go",
    ".rs", ".json", ".md"
)

EXCLUDED_DIRS = {
    "node_modules",
    ".git",
    "venv",
    "__pycache__",
    "dist",
    "build",
    ".next",
    ".idea",
    "test",
    "tests",
    "samples",
    "resources"
}


def retrieve_relevant_chunks(question, project_id):

    # ==============================
    # 🟢 MODE 1 — OpenAI Embedding Search
    # ==============================
    if settings.USE_OPENAI:

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        response = client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=question
        )

        query_embedding = response.data[0].embedding

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=TOP_K,
            where={"project_id": project_id}
        )

        if not results.get("documents") or not results["documents"][0]:
            return []

        documents = results["documents"][0]
        metadatas = results.get("metadatas", [[]])[0]

        chunks = []

        for doc, meta in zip(documents, metadatas):

            if not doc or not doc.strip():
                continue

            chunks.append({
                "file_path": meta.get("file_path"),
                "content": doc,
                "start_line": meta.get("start_line"),
                "end_line": meta.get("end_line")
            })

        return chunks[:5]

    # ==============================
    # 🔵 MODE 2 — Optimized Smart Local Search
    # ==============================
    else:

        upload_dir = os.path.join("uploads", project_id)

        if not os.path.exists(upload_dir):
            return []

        keywords = [k for k in question.lower().split() if len(k) > 2]

        matches = []
        MAX_FILES = 400
        file_counter = 0

        for root, dirs, files in os.walk(upload_dir):

            # 🔥 limit directory depth
            depth = root.replace(upload_dir, "").count(os.sep)
            if depth > 4:
                continue

            # 🔥 remove heavy dirs
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

            for file in files:

                if not file.endswith(SUPPORTED_EXTENSIONS):
                    continue

                file_counter += 1
                if file_counter > MAX_FILES:
                    break

                full_path = os.path.join(root, file)

                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    lower_content = content.lower()
                    score = 0

                    # 🔥 keyword frequency scoring
                    for keyword in keywords:
                        score += lower_content.count(keyword) * 3

                    # 🔥 boost important backend files
                    file_lower = full_path.lower()
                    if any(k in file_lower for k in [
                        "server", "controller", "route",
                        "middleware", "auth", "model"
                    ]):
                        score += 5

                    if score > 0:
                        matches.append({
                            "file_path": full_path,
                            "content": content,
                            "score": score
                        })

                except Exception:
                    continue

            if file_counter > MAX_FILES:
                break

        # 🔥 Sort by relevance score
        matches.sort(key=lambda x: x["score"], reverse=True)

        top_matches = matches[:TOP_K]

        smart_chunks = []

        for match in top_matches:

            content = match["content"]
            lines = content.split("\n")

            relevant_lines = [
                line for line in lines
                if any(keyword in line.lower() for keyword in keywords)
            ]

            snippet = "\n".join(relevant_lines[:20])

            if snippet.strip():
                smart_chunks.append({
                    "file_path": match["file_path"],
                    "content": snippet,
                    "start_line": None,
                    "end_line": None
                })

        return smart_chunks[:5]
