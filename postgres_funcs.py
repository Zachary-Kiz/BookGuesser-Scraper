import json
import os
import psycopg2
import subprocess

from dotenv import load_dotenv
from datetime import date, timedelta
from psycopg2.extras import RealDictCursor

load_dotenv('.rds.env')
POSTGRESQL_USER = os.getenv('POSTGRESQL_USER')
POSTGRESQL_DATABASE = os.getenv('POSTGRESQL_DATABASE')
DB_HOSTNAME = os.getenv('DB_HOSTNAME')
AWS_BUCKET = os.getenv('AWS_BUCKET')
AWS_PWD = os.getenv('AWS_PWD')
    

connection = psycopg2.connect(
    user=POSTGRESQL_USER, 
    password=AWS_PWD, 
    host=DB_HOSTNAME, 
    port=5432, 
    database=POSTGRESQL_DATABASE, 
    cursor_factory=RealDictCursor, 
    sslmode='verify-full',
    sslrootcert='./global-bundle.pem'
    )
cursor = connection.cursor()

def sql_get_book():
    cursor.execute("""
                   SELECT * FROM bookData 
                   WHERE downloaded = FALSE
                   ORDER BY RANDOM()
                   LIMIT 1
                   """)

    record = cursor.fetchone()

    return record

def sql_upload_book(record, book_data, img_data):

    if book_data is None:
        raise Exception("Book not pulled from DB")
    
    cursor.execute(
        "INSERT INTO books (title, author, releaseYear, genre) VALUES (%s, %s, %s, %s)",
        (
            book_data['title'],
            book_data['author_name'],
            book_data.get('first_publish_year'),
            book_data['genre']
        )
    )

    cursor.execute(
        "SELECT * FROM books WHERE title = %s",
        (book_data['title'],)
    )

    book = cursor.fetchone()
    
    if book is None:
        raise Exception("Book not uploaded to Postgres")

    if len(img_data) != 7:
        raise Exception("Image levels not generated correctly")

    for cover in img_data:
        url = "https://{bucket}.s3.us-east-2.amazonaws.com/{id}/level_{level}.jpg".format(bucket=AWS_BUCKET, id=cover['cover_id'], level=cover['level'])
        cursor.execute(
            "INSERT INTO covers (book_id, level, image_url) VALUES (%s, %s, %s)",
            (
                book['id'],
                cover['level'],
                url
            )
        )

    one_week_from_today = date.today() + timedelta(days=7)
    
    cursor.execute(
        "INSERT INTO daily_puzzle (puzzle_date, book_id) VALUES (%s, %s)",
        (
            one_week_from_today,
            book['id']
        )
    )

    cursor.execute(f"UPDATE bookData SET downloaded = TRUE WHERE id = {record['id']}")
    
    connection.commit()
    print("COMPLETE!!")

def handleError(book):
    cursor.execute(f"UPDATE bookData SET downloaded = TRUE WHERE title = {book}")
    newBook = sql_get_book()
    return newBook
