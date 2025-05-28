-- Enable AI extension
CREATE EXTENSION IF NOT EXISTS ai CASCADE;

ALTER TABLE documents ADD COLUMN IF NOT EXISTS embedding vector(1536);

-- Generate embeddings for all documents
UPDATE documents
SET embedding = ai.openai_embed(
    'text-embedding-3-small',
    text
);

CREATE INDEX IF NOT EXISTS idx_document_embedding ON documents USING ivfflat (embedding vector_cosine_ops);
