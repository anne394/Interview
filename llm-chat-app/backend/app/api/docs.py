from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import models
from app.rag import embeddings, retriever
from typing import List
import io

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload-text")
def upload_text_file(title: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type not in ("text/plain", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Only plain text files supported in this minimal demo")
    content = io.TextIOWrapper(file.file, encoding="utf-8").read()
    doc = models.Document(title=title, text=content)
    db.add(doc); db.commit(); db.refresh(doc)

    # Simple chunking: split by paragraphs of ~800 chars
    chunks = []
    max_chunk = 800
    text = content
    i = 0
    while i < len(text):
        chunk = text[i : i + max_chunk]
        chunks.append(chunk)
        i += max_chunk

    # create embeddings and add to qdrant
    docs_for_qdrant = []
    for idx, chunk in enumerate(chunks):
        emb = embeddings.embed_text_via_gemini(chunk)
        docs_for_qdrant.append({"id": f"{doc.id}-{idx}", "text": chunk, "embedding": emb, "meta": {"doc_id": doc.id, "title": title}})

    retriever.add_documents_to_qdrant(docs_for_qdrant, vector_size=len(docs_for_qdrant[0]["embedding"]) if docs_for_qdrant else 1536)
    return {"ok": True, "doc_id": doc.id, "chunks": len(chunks)}
