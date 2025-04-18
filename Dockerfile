# ---------- Stage 1: Builder ----------
FROM python:3.13-slim AS builder

WORKDIR /app

# System dependencies for scientific libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies into a clean target dir
RUN pip install --upgrade pip && \
    pip install --prefix=/install "fastapi[standard]" && \
    pip install --prefix=/install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install --prefix=/install -r requirements.txt

# ---------- Stage 2: Runtime ----------
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

EXPOSE 8080

CMD ["bash", "-c", "echo \"$FIREBASE_ADMIN_KEY\" > serviceAccountKey.json && python src/server.py"]
