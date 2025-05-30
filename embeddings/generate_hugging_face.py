from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from typing import List
import psycopg2
from tqdm import tqdm

from config.db import DB_CONFIG

# loads https://huggingface.co/BAAI/bge-small-en-v1.5
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

if __name__ == "__main__":
    # Connect to your PostgreSQL database
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Add the embeddings column if it doesn't exist
    cur.execute("""
        ALTER TABLE documents ADD COLUMN IF NOT EXISTS embedding vector(384);
    """)
    conn.commit()

    # Fetch all rows with their id and text
    cur.execute("SELECT id, text FROM documents;")
    rows = cur.fetchall()

    # Generate embeddings and update the table
    for row in tqdm(rows):
        doc_id, text = row
        embedding = embed_model.get_text_embedding(text)
        cur.execute(
            "UPDATE documents SET embedding = %s WHERE id = %s;",
            (embedding, doc_id)
        )

    conn.commit()

    cur.execute("CREATE INDEX IF NOT EXISTS idx_document_embedding ON documents USING ivfflat (embedding vector_cosine_ops);")
    conn.commit()
    cur.close()
    conn.close()
