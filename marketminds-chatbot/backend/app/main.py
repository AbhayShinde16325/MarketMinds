"""
MarketMinds FastAPI Backend
"""

from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.app.chatbot.response_builder import ResponseBuilder
from backend.app.llm.llm_client import OllamaLLMClient


app = FastAPI(
    title="MarketMinds API",
    description="Local RAG-powered financial chatbot backend",
    version="0.1.0",
)

# ---------- Frontend setup ----------
BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = BASE_DIR / "frontend"

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")


# ---------- Core system ----------
llm_client = OllamaLLMClient(model_name="mistral")
response_builder = ResponseBuilder(llm_client)


# ---------- API models ----------
class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str


# ---------- Health ----------
@app.get("/health")
def health_check():
    return {"status": "ok"}


# ---------- Chat endpoint ----------
@app.post("/ask", response_model=QueryResponse)
def ask_question(request: QueryRequest):
    answer = response_builder.build_response(request.question)
    return QueryResponse(answer=answer)
