import psycopg2
from datasets import load_dataset
from tqdm import tqdm

from config.db import DB_CONFIG, TABLE_NAME

LIMIT = 1000

if __name__ == "__main__":
    # === STEP 1: LOAD DATASET FOR STREAMING ===
    print("Loading dataset from Hugging Face...")
    dataset = load_dataset("BeIR/trec-news-generated-queries", "default", streaming=True)['train']

    # === STEP 2: CONNECT TO POSTGRES ===
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # === STEP 3: CREATE TABLE ===
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        text TEXT NOT NULL,
        query TEXT
    );
    """
    cur.execute(create_table_sql)
    conn.commit()

    # === STEP 4: INSERT DATA ===
    insert_sql = f"INSERT INTO {TABLE_NAME} (id, title, text, query) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;"
    i = 0
    for item in tqdm(dataset, total=LIMIT, desc="Inserting data into PostgreSQL"):
        if i >= LIMIT:
            break
        id = item.get("_id", "")
        title = item.get("title", "")
        text = item.get("text", "")
        query = item.get("query", "")
        if not id or not title or not text:
            continue  # Skip items without essential fields
        cur.execute(insert_sql, (id, title, text, query))
        i += 1

    conn.commit()
    cur.close()
    conn.close()
    print("Done.")
