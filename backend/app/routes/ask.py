from fastapi import APIRouter
from pydantic import BaseModel
from app.services.retrieval_service import retrieve_relevant_chunks
from app.services.qa_service import generate_answer
from app.database import SessionLocal
from app.models import QAHistory

router = APIRouter(prefix="/ask", tags=["Ask"])


class QuestionRequest(BaseModel):
    project_id: str
    question: str


@router.post("/")
def ask_question(request: QuestionRequest):

    if not request.project_id or not request.question:
        return {"error": "project_id and question required"}

    # Step 1: Retrieve relevant chunks
    retrieved_chunks = retrieve_relevant_chunks(
        request.question,
        request.project_id
    )

    if not retrieved_chunks:
        return {"error": "No relevant code found"}

    # Step 2: Generate answer
    # IMPORTANT: generate_answer expects list of strings
    answer = generate_answer(
        request.question,
        [c.get("content") for c in retrieved_chunks if isinstance(c, dict)]
    )

    # Step 3: Save Q&A to database
    db = SessionLocal()
    try:
        qa_entry = QAHistory(
            project_id=request.project_id,
            question=request.question,
            answer=answer
        )
        db.add(qa_entry)
        db.commit()
    finally:
        db.close()

    # Step 4: Return structured response
    return {
        "answer": answer,
        "sources": [
            {
                "file_path": c.get("file_path"),
                "start_line": c.get("start_line"),
                "end_line": c.get("end_line"),
                "snippet": c.get("content")
            }
            for c in retrieved_chunks
            if isinstance(c, dict)
        ]
    }
