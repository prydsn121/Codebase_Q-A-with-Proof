from sqlalchemy import Column, Integer, String, Text
from app.database import Base


class QAHistory(Base):
    __tablename__ = "qa_history"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String)
    question = Column(Text)
    answer = Column(Text)
