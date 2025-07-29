FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Clone and install GUI-Actor
RUN git clone https://github.com/microsoft/GUI-Actor.git /tmp/gui-actor \
    && cd /tmp/gui-actor \
    && pip install -e . \
    && cd /app \
    && rm -rf /tmp/gui-actor

# Copy application files
COPY main.py .
COPY start_server.py .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command
CMD ["python", "start_server.py", "--host", "0.0.0.0", "--port", "8080"] 