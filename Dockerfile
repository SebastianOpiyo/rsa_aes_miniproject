# API server
FROM python:3.8-slim

WORKDIR /app

COPY apiServer/* ./
COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY api.py ./

CMD ["python", "api.py"]

# API consumer client
FROM python:3.8-slim

WORKDIR /app

COPY client/* ./
COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY client.py ./

CMD ["python", "client.py"]
