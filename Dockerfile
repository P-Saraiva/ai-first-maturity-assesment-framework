FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libgtk-3-0 \
    libasound2 \
    libgbm1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxshmfence1 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz-icu0 \
    libwebp-dev \
    libjpeg-dev \
    libvpx-dev \
    libopus-dev \
    libwoff1 \
    libgl1 \
    libgles2 \
    libcurl4 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Install Playwright browsers
RUN python -m playwright install

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data/exports static/uploads backups instance

# Expose port
EXPOSE 5001

# Environment variables
ENV FLASK_APP=run.py \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL=sqlite:///instance/app_dev.db \
    WORKERS=2 \
    THREADS=2

# Entrypoint script for proper signal handling
COPY scripts/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]