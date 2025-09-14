import requests
from app.core.config import settings

def embed_text_via_gemini(text: str) -> list[float]:
    """
    Generic wrapper to call a Gemini-compatible embedding endpoint.
    You must provide GEMINI_API_KEY and GEMINI_API_URL in env.
    This assumes provider accepts JSON: {"model": "...", "input": "..."} and returns embedding in result["embedding"].
    Adjust to match your actual provider's API shape.
    """
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set")

    url = f"{settings.GEMINI_API_URL.rstrip('/')}/embeddings"
    payload = {"model": settings.EMBEDDING_MODEL, "input": text}
    headers = {"Authorization": f"Bearer {settings.GEMINI_API_KEY}", "Content-Type": "application/json"}
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # Try a couple of common shapes: adjust as needed
    if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
        # e.g., OpenAI style: data[0].embedding
        return data["data"][0]["embedding"]
    if "embedding" in data:
        return data["embedding"]
    # fallback if provider returns top-level list
    if isinstance(data, list):
        return data[0]
    raise RuntimeError("Unexpected embedding response shape: " + str(data))
