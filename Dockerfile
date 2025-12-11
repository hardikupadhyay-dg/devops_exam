FROM public.ecr.aws/lambda/python:3.11

COPY lambda_function.py ${LAMBDA_TASK_ROOT}/

ENV DDB_TABLE=DG_Events

CMD ["lambda_function.lambda_handler"]
