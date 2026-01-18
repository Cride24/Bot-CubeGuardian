# Dockerfile pour Bot CubeGuardian - Version Python natif
# Image multi-stage pour optimiser la taille et la sécurité

# Stage de build
FROM python:3.11-slim as builder

# Installation des dépendances de build
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage de production
FROM python:3.11-slim

# Installation des dépendances système minimales
RUN apt-get update && apt-get install -y \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Création de l'utilisateur non-root
RUN useradd --create-home --shell /bin/bash cubeguardian

# Copie des dépendances Python depuis le stage de build vers le répertoire utilisateur
COPY --from=builder /root/.local /home/cubeguardian/.local
RUN chown -R cubeguardian:cubeguardian /home/cubeguardian/.local

USER cubeguardian
WORKDIR /home/cubeguardian

# Copie du code
COPY --chown=cubeguardian:cubeguardian . .

# Configuration des logs et permissions
RUN mkdir -p logs keys && \
    chmod 755 logs && \
    chmod 700 keys

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/home/cubeguardian
ENV PATH=/home/cubeguardian/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Point d'entrée
CMD ["python", "-m", "src.bot"]
