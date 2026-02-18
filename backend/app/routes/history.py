from fastapi import APIRouter
from app.database import SessionLocal
from app.models import QAHistory

router = APIRouter(prefix="/history", tags=["History"])


@router.get("/{project_id}")
def get_history(project_id: str):
    db = SessionLocal()

    try:
        results = (
            db.query(QAHistory)
            .filter(QAHistory.project_id == project_id)
            .order_by(QAHistory.id.desc())
            .limit(10)
            .all()
        )

        if not results:
            return {"message": "No history found for this project"}

        return [
            {
                "question": r.question,
                "answer": r.answer,
                # If you later add timestamp column:
                # "created_at": r.created_at
            }
            for r in results
        ]

    finally:
        db.close()
