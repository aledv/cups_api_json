FROM python:3.11-slim

# Installa dipendenze di sistema per CUPS
RUN apt-get update && apt-get install -y \
    libcups2-dev \
    gcc \
    g++ \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Crea directory di lavoro
WORKDIR /app

# Copia requirements
COPY requirements.txt .

# Installa dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice dell'applicazione
COPY app.py .

# Esponi la porta
EXPOSE 5001

# Crea un utente non-root per sicurezza
RUN useradd -m -u 1000 cupsmonitor
USER cupsmonitor

# Comando di avvio
CMD ["python", "app.py"]
