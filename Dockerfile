FROM python:3.9-slim

WORKDIR /app

RUN pip install "fastapi[standard]"

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . /app


CMD ["fastapi", "run", "src/server.py", "--port", "8000"]