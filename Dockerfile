FROM python:3.13.3-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installation d'uv directement 
RUN pip install uv

# Dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    gcc \
    libjpeg-dev \ 
    zlib1g-dev \  
    libwebp-dev \ 
    && rm -rf /var/lib/apt/lists/*

# Création du répertoire de cache 
RUN mkdir -p /app/cache && chmod 777 /app/cache

# Copie des requirements et installation
COPY requirements.txt .
RUN uv pip install -r requirements.txt

# Copie du code source
COPY . .

EXPOSE 8000

CMD ["./entrypoint.sh"]