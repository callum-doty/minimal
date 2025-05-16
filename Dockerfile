FROM python:3.9-slim

# Set environment variables
ENV PYTHONPATH=/app \
    FLASK_APP=src/wsgi.py \ 
    FLASK_ENV=production \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create the app directory first
RUN mkdir -p /app/src

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    gcc \
    python3-dev \
    libpoppler-dev \
    build-essential \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    libleptonica-dev \
    pkg-config \
    python3-magic \
    libmagic1 \
    zlib1g-dev \
    libmagic-dev \
    postgresql-client \
    libjpeg-dev \
    libopenjp2-7-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt /app/

# Install Python packages
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy source code
COPY src /app/src
COPY migrations /app/migrations
COPY gunicorn.conf.py start.sh /app/

# Create necessary directories
RUN mkdir -p /app/uploads /app/logs /app/data/documents /app/tmp

# Make the start script executable
RUN chmod +x /app/start.sh

# Set working directory
WORKDIR /app

# Create a non-root user
RUN useradd -m appuser && chown -R appuser /app

# Switch to non-root user
USER appuser

# Health check (Render will use its own health check via the URL)
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT:-5000}/health || exit 1

# Expose the dynamic port from environment (but still define a default)
ENV HOST=0.0.0.0
ENV PORT=5000
EXPOSE ${PORT}
# Use the start script
CMD ["./start.sh"]