FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Pillow dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    netcat-traditional \
    python3-dev \
    libjpeg-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create .env file from environment variables
RUN echo "DEBUG=\${DEBUG}" > .env && \
    echo "ALLOWED_HOSTS=\${ALLOWED_HOSTS}" >> .env && \
    echo "CORS_ALLOWED_ORIGINS=\${CORS_ALLOWED_ORIGINS}" >> .env && \
    echo "DB_NAME=\${DB_NAME}" >> .env && \
    echo "DB_USER=\${DB_USER}" >> .env && \
    echo "DB_PASSWORD=\${DB_PASSWORD}" >> .env && \
    echo "DB_HOST=\${DB_HOST}" >> .env && \
    echo "DB_PORT=\${DB_PORT}" >> .env

# Make the script executable
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8000

# Use the entrypoint script
ENTRYPOINT ["./entrypoint.sh"]