FROM public.ecr.aws/lambda/python:3.8

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

COPY postgres_funcs.py ${LAMBDA_TASK_ROOT}
COPY global-bundle.pem ${LAMBDA_TASK_ROOT}

CMD [ "postgres_funcs.lambda_handler" ]