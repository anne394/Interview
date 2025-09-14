from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.db.session import SessionLocal
from app.db import models
from sqlalchemy.orm import Session
from app.core.security import decode_token
from app.rag import embeddings, retriever
import google.generativeai as genai

router = APIRouter()

class AskIn(BaseModel):
    query: str
    conversation_id: int | None = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/ask")
def ask(req: AskIn, authorization: str | None = None, db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
        username = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    # 1. Embed query (Gemini embeddings, your embeddings.py should wrap this)
    q_emb = embeddings.embed_text_via_gemini(req.query)

    # 2. Retrieve docs from Qdrant
    hits = retriever.semantic_search(q_emb, limit=3)
    context_texts = [h["text"] for h in hits if h.get("text")]

    # 3. Build prompt
    system_prompt = "You are a helpful assistant. Use only information from the provided context if relevant."
    prompt = system_prompt + "\n\nContext:\n" + "\n\n---\n\n".join(context_texts) + f"\n\nUser: {req.query}\nAssistant:"

    # 4. Call Gemini for response
    answer = call_gemini_completion(prompt)

    # 5. Store conversation + messages
    conv = None
    if req.conversation_id:
        conv = db.query(models.Conversation).filter(
            models.Conversation.id == req.conversation_id,
            models.Conversation.user_id == user.id
        ).first()
    if not conv:
        conv = models.Conversation(user_id=user.id)
        db.add(conv)
        db.commit()
        db.refresh(conv)

    um = models.Message(conversation_id=conv.id, role="user", text=req.query)
    am = models.Message(conversation_id=conv.id, role="assistant", text=answer)
    db.add_all([um, am])
    db.commit()

    return {
        "answer": answer,
        "conversation_id": conv.id,
        "sources": [{"id": h["id"], "score": h["score"]} for h in hits]
    }

def call_gemini_completion(prompt: str) -> str:
    """
    Uses Gemini SDK to generate content.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text
