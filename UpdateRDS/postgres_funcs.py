import json
import os
import boto3
import psycopg2

from datetime import date, timedelta
from psycopg2.extras import RealDictCursor

POSTGRESQL_USER = os.environ['POSTGRESQL_USER']
POSTGRESQL_DATABASE = os.environ['POSTGRESQL_DATABASE']
DB_HOSTNAME = os.environ['DB_HOSTNAME']
AWS_BUCKET = os.environ['AWS_BUCKET']
AWS_PWD = os.environ['AWS_PWD']
    
lambda_client = boto3.client("lambda")

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

def sql_upload_book(record, book_data, img_data, days=7):

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

    one_week_from_today = date.today() + timedelta(days=days)
    
    cursor.execute(
        "INSERT INTO daily_puzzle (puzzle_date, book_id) VALUES (%s, %s)",
        (
            one_week_from_today,
            book['id']
        )
    )

    cursor.execute("UPDATE bookData SET downloaded = TRUE WHERE id = %s", (record['id'],))
    
    connection.commit()
    print("COMPLETE!!")


def handleError(book):
    cursor.execute("UPDATE bookData SET downloaded = TRUE WHERE title = %s", (book,))
    upload()

def upload():
    book = sql_get_book()

    response = lambda_client.invoke(
        FunctionName="UploadImages",
        InvocationType="RequestResponse",
        Payload=json.dumps(book)
    )

    response_payload = json.loads(
        response["Payload"].read()
    )

    if response_payload['statusCode'] != 200:
        handleError(book['title'])
        return
    
    return response_payload['body']

def lambda_handler(event, context):
    
    days = 7

    if 'days' in event:
        days = event['days']
    
    body = upload()
    
    sql_upload_book(body['book'], body['book_data'], body['img_data'], days)
    return {"statusCode" : 200}
