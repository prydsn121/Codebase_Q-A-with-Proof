from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routes import upload, ask, status,history
from app.database import engine, Base


# Lifespan event (runs on startup)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create DB tables on startup
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
    yield
    # (Optional cleanup can go here)


app = FastAPI(
    title="Codebase Q&A API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(ask.router)
app.include_router(status.router)
app.include_router(history.router)


@app.get("/")
def root():
    return {"message": "Codebase Q&A API running"}
