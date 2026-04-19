import os
import psycopg2

from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor


load_dotenv()

POSTGRESQL_DATABASE = os.getenv('POSTGRESQL_DATABASE')
POSTGRESQL_USER = os.getenv('POSTGRESQL_USER')
POSTGRESQL_PWD = os.getenv('POSTGRESQL_PWD')

connection = psycopg2.connect(database=POSTGRESQL_DATABASE, user=POSTGRESQL_USER, password=POSTGRESQL_PWD, port=5432, cursor_factory=RealDictCursor)

def sql_get_book():
    cursor = connection.cursor()
    cursor.execute("""
                   SELECT * FROM bookData 
                   WHERE downloaded = FALSE
                   ORDER BY RANDOM()
                   LIMIT 1
                   """)

    # Fetch all rows from database
    record = cursor.fetchone()

    return record
