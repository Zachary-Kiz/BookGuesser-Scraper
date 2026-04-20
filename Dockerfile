FROM python:3.14-slim
WORKDIR /usr/local/bookguesser

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y libgl1 libglib2.0-0

COPY download_books.py ./
COPY postgres_funcs.py ./

RUN mkdir /image
RUN mkdir /processed

CMD ["python", "download_books.py"]