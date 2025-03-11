import openai
import json
from sqlalchemy.sql import text
from ..db.db import get_db
from clio.markdown import render_markdown
from clio.state import app_state
from clio.logging import log_message

# OpenAI Model Name
EMBEDDING_MODEL = "text-embedding-ada-002"

def generate_embedding(record_uuid: str):
    """Generate and store OpenAI embeddings for a record."""
    
    # ✅ Step 1: Fetch the record content
    with next(get_db()) as db:
        query = text("SELECT content_schema FROM record WHERE UUID = :uuid")
        result = db.execute(query, {"uuid": record_uuid}).fetchone()
    
    if not result:
        log_message(f"Error: Record {record_uuid} not found.", "error")
        return None
    
    markdown_text = render_markdown(result["content_schema"])  # ✅ Convert to Markdown

    # ✅ Step 2: Call OpenAI API to generate embedding
    openai.api_key = "YOUR_OPENAI_API_KEY"
    
    try:
        response = openai.Embedding.create(
            model=EMBEDDING_MODEL,
            input=markdown_text
        )
        embedding_vector = response["data"][0]["embedding"]

    except Exception as e:
        log_message(f"OpenAI API Error: {e}", "error")
        return None

    # ✅ Step 3: Store embedding in the database
    with next(get_db()) as db:
        insert_query = text("""
            INSERT INTO embeddings (rec_UUID, embedding, model)
            VALUES (:uuid, :embedding, :model)
            ON DUPLICATE KEY UPDATE embedding = :embedding, model = :model;
        """)
        db.execute(insert_query, {
            "uuid": record_uuid,
            "embedding": json.dumps(embedding_vector),
            "model": EMBEDDING_MODEL
        })
        db.commit()

    log_message(f"Stored embedding for {record_uuid}", "info")
    return embedding_vecto

