# API consumer client
FROM python:3.10-slim-bullseye

ENV TZ=Africa/Nairobi
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONIOENCODING UTF-8

WORKDIR /app

COPY requirements.txt .
ARG PIP_TRUSTED_HOST=127.0.0.1
ARG PIP_INDEX_URL=https://pypi.python.org/simple/
RUN pip3 install --quiet --no-cache-dir -r requirements.txt

COPY client/ .

EXPOSE 5000

CMD ["python", "client.py"]
