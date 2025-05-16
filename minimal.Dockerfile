FROM python:3.9-slim

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create app directory
WORKDIR /app

# Copy only the necessary files
COPY direct.py /app/
COPY direct-start.sh /app/
COPY requirements.txt /app/

# Install minimal dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Make the start script executable
RUN chmod +x /app/direct-start.sh

# Create a non-root user
RUN useradd -m appuser && chown -R appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT:-5000}/health || exit 1

# Expose the dynamic port from environment
ENV PORT=5000
EXPOSE ${PORT}

# Use the direct start script
CMD ["./direct-start.sh"]
