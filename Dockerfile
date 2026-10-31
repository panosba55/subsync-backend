FROM python:3.11-slim

# Εγκατάσταση του ffmpeg στο Linux περιβάλλον
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY sync_server.py .

# Εκκίνηση του server διαβάζοντας τη θύρα του cloud παρόχου
CMD ["sh", "-c", "uvicorn sync_server:app --host 0.0.0.0 --port ${PORT:-8000}"]