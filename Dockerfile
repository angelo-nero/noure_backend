FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including netcat-traditional
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make the script executable
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8000

# Use the entrypoint script
ENTRYPOINT ["./entrypoint.sh"]