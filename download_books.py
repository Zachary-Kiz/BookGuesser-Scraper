import requests
import cv2
import pytesseract
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

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

pixelLevels = [20, 15, 12, 10, 8, 5]

def get_books(query="fantasy", limit=10):
    url = f"https://openlibrary.org/search.json?q={query}&limit={limit}"
    res = requests.get(url)
    data = res.json()
    
    book_data = []
    all_books = data['docs']
    for book in all_books:
        book_data.append({
            "author_name" : ",".join(book['author_name']),
            "first_publish_year": book["first_publish_year"],
            "title": book["title"],
            "cover_i": book["cover_i"]
        })
    return book_data

def get_cover_url(cover_id):
    return f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"

def download_covers(book_data):
    paths = {}
    for book in book_data:
        url = get_cover_url(book['cover_i'])
        img = requests.get(url).content

        cover_id = book['cover_i']
        path = f"image/{cover_id}.jpg"
        with open(path, "wb") as f:
            f.write(img)
        paths[cover_id] = path
    return paths


def generate_levels(paths):
    img_paths = []
    for cover_id in paths:
        
        image_path = paths[cover_id]
        img = cv2.imread(image_path)
        height, width = img.shape[:2]

        for i, pixelSize in enumerate(pixelLevels):
            w, h = (width // pixelSize, height // pixelSize)
            temp = cv2.resize(img, (w,h), interpolation=cv2.INTER_LINEAR)

            output = cv2.resize(temp, (width, height), interpolation=cv2.INTER_NEAREST)

            path = f"processed/{cover_id}_level_{i}.jpg"
            cv2.imwrite(path, output)
            img_paths.append((f"{cover_id}/level_{i}.jpg", path))
    return img_paths

def upload_img(paths):
    for path in paths:
        client.upload_file(
            Filename=path[1],
            Bucket=AWS_BUCKET,
            Key=path[0]
        )
    

book_data = get_books()
paths = download_covers(book_data)
new_paths = generate_levels(paths)
upload_img(new_paths)
