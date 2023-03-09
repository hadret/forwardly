# syntax=docker/dockerfile:1
FROM python:3.11-slim
LABEL org.opencontainers.image.source https://github.com/hadret/forwardly

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./main.py /code/main.py

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
