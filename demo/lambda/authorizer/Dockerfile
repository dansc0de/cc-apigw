FROM public.ecr.aws/lambda/python:3.12

COPY authorizer.py ${LAMBDA_TASK_ROOT}/

CMD ["authorizer.lambda_handler"]
