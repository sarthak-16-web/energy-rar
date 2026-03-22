import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import UPLOAD_DIR, CHROMA_DIR
from app.utils import extract_text_from_pdf
from app.rag import ingest_document, answer_question

app = FastAPI(title="Energy Document RAG")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {"message": "Backend is running"}


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_path = os.path.join(UPLOAD_DIR, "uploaded.pdf")

    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = extract_text_from_pdf(file_path)

    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    ingest_document(text)

    return {"message": "PDF uploaded and processed successfully"}


@app.post("/ask")
def ask_question(payload: QuestionRequest):
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question is required")

    answer = answer_question(payload.question)
    return {"answer": answer}