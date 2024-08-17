import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        print("Successfully connected to the database!")
        
        # Create a cursor and execute a simple query
        cur = conn.cursor()
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        print(f"PostgreSQL database version: {db_version[0]}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Unable to connect to the database. Error: {e}")

if __name__ == "__main__":
    test_connection()