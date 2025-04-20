FROM python:3.9-slim

WORKDIR /app

RUN pip install "fastapi[standard]"

# Install CPU-only torch manually
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8080
ENV PYTHONPATH=/app/src

CMD ["bash", "-c", "echo \"$FIREBASE_ADMIN_KEY\" > serviceAccountKey.json && uvicorn src.server:app --host 0.0.0.0 --port 8080"]
