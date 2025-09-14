from fastapi import FastAPI
from app.db.session import engine, SessionLocal
from app.db import models
from app.api import auth, docs, chat
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("AIzaSyAe5uTPi2ZgLQuATMIyo7l-ppjeGdGLE_4"))


# create tables (simple startup; production: use alembic)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="LLM Chat with RAG")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(docs.router, prefix="/docs", tags=["docs"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])

@app.get("/")
def health():
    return {"status": "ok"}
