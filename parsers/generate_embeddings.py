import os
import psycopg2

from config.db import DB_CONFIG

def run_sql_file(db_path, sql_file_path):
    with open(sql_file_path, 'r') as file:
        sql_script = file.read()
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute(sql_script)
        conn.commit()
        print("SQL script executed successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # Adjust the database path as needed
    db_path = os.path.join(os.path.dirname(__file__), '..', 'your_database.db')
    sql_file_path = os.path.join(os.path.dirname(__file__), '../sql', 'generate_embeddings.sql')
    run_sql_file(db_path, sql_file_path)