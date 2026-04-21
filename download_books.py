import requests
import cv2
import pytesseract
import boto3
import os
from dotenv import load_dotenv

from postgres_funcs import sql_get_book, sql_upload_book

load_dotenv('.env')

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_BUCKET = os.getenv('AWS_BUCKET')

client = boto3.client(
    service_name="s3", 
    region_name="eu-central-1", 
    aws_access_key_id=AWS_ACCESS_KEY_ID, 
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

pixelLevels = [20, 15, 12, 10, 8, 5, 1]

def get_book(query, limit=10):
    url = f"https://openlibrary.org/search.json?q={query}&limit={limit}"
    res = requests.get(url)
    data = res.json()
    
    all_books = data['docs']
    for book in all_books:
        if query == book["title"]:
            book_data = {
                "author_name" : ",".join(book['author_name']),
                "first_publish_year": book["first_publish_year"],
                "title": book["title"],
                "cover_i": book["cover_i"]
            }
            break
    return book_data

def get_cover_url(cover_id):
    return f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"

def download_covers(book_data):
    paths = {}
    url = get_cover_url(book_data['cover_i'])
    img = requests.get(url).content

    cover_id = book_data['cover_i']
    path = f"image/{cover_id}.jpg"
    with open(path, "wb") as f:
        f.write(img)
    paths[cover_id] = path
    return paths


def generate_levels(paths):
    img_data = []
    for cover_id in paths:
        
        image_path = paths[cover_id]
        img = cv2.imread(image_path)
        height, width = img.shape[:2]

        for i, pixelSize in enumerate(pixelLevels):
            w, h = (width // pixelSize, height // pixelSize)
            temp = cv2.resize(img, (w,h), interpolation=cv2.INTER_LINEAR)

            output = cv2.resize(temp, (width, height), interpolation=cv2.INTER_NEAREST)

            level = i + 1
            path = f"processed/{cover_id}_level_{level}.jpg"
            cv2.imwrite(path, output)
            img_data.append({
                "cover_id": cover_id,
                "path": path,
                "level": level
            })
    return img_data

def get_key(data):
    return f"{data['cover_id']}/level_{data['level']}.jpg"

def upload_img(img_data):
    for data in img_data:
        key = get_key(data)
        client.upload_file(
            Filename=data['path'],
            Bucket=AWS_BUCKET,
            Key=key,
            ExtraArgs={
                "ContentType": "image/jpeg"
            }
        )
    
if __name__ == "__main__":
    book = sql_get_book()
    book_data = get_book(book['title'])
    paths = download_covers(book_data)
    img_data = generate_levels(paths)
    upload_img(img_data)
    sql_upload_book(book_data, img_data)
