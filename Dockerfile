FROM python:3.11-slim
WORKDIR /code
RUN pip install --no-cache-dir fastapi uvicorn jinja2 python-multipart
COPY ./app /code/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

