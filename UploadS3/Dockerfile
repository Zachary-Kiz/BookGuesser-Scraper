FROM public.ecr.aws/lambda/python:3.8

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

RUN rpm -Uvh https://archives.fedoraproject.org/pub/archive/epel/7/x86_64/Packages/e/epel-release-7-14.noarch.rpm
RUN yum -y update
RUN yum install -y \
    tesseract \
    libgl1 \
    libglib2.0-0

COPY download_books.py ${LAMBDA_TASK_ROOT}

CMD [ "download_books.lambda_handler" ]