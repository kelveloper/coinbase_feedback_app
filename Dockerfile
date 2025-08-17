# Advanced Trade Insight Engine - Docker Configuration
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create output directory
RUN mkdir -p output

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Default command - run dashboard
CMD ["streamlit", "run", "src/dashboard/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]