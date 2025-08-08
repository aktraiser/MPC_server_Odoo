# Use Python 3.11 slim image for better compatibility with MCP
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Cache bust - force rebuild
ENV CACHE_BUST=2025-01-17-v2
ARG REBUILD_CACHE=1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libssl-dev \
        libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Clean any potential cached files
RUN rm -rf /app/odoo_mcp_server 2>/dev/null || true

# Copy application code
COPY odoo_mcp_server/ ./odoo_mcp_server/

# Ensure no old server.py exists
RUN rm -f /app/odoo_mcp_server/server.py 2>/dev/null || true
# Pas de copie d'exemple d'env par défaut; utilisez les variables d'environnement du runtime

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import odoo_mcp_server; print('OK')" || exit 1

# Run the application
CMD ["python", "-m", "odoo_mcp_server"]