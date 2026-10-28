# Imagen de la app del TP.
# Etapa "dev": desarrollo local con pruebas.
# Etapa "prod" (la final, por defecto): solo lo necesario para servir la app web.

FROM python:3.13-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8501
WORKDIR /app
# Chromium: kaleido lo usa para exportar las figuras a PNG (botón "Todas las figuras").
RUN apt-get update \
    && apt-get install -y --no-install-recommends chromium \
    && rm -rf /var/lib/apt/lists/*
ENV BROWSER_PATH=/usr/bin/chromium
COPY requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://localhost:{os.environ[\"PORT\"]}/_stcore/health')"
# Forma shell para que ${PORT} lo pueda definir la plataforma de despliegue (Render, Cloud Run...).
CMD streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0

# --- Desarrollo: herramientas de prueba ---
FROM base AS dev
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt
COPY . .

# --- Producción: código de la app y usuario sin privilegios ---
FROM base AS prod
COPY . .
RUN useradd --create-home app && chown -R app /app
USER app
