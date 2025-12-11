FROM public.ecr.aws/lambda/python:3.11

# Copy function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}/

# If you need external packages, include requirements.txt and uncomment:
# COPY requirements.txt .
# RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Set env var default (overridden by Lambda config)
ENV DDB_TABLE=DG_Events

# Set the Lambda handler
CMD ["lambda_function.lambda_handler"]
