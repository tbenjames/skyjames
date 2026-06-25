# SkyJames - Production Docker Container
FROM python:3.12-slim

LABEL maintainer="SkyJames AI"
LABEL version="2.0.0"
LABEL description="SkyJames - Production Computer Vision Pipeline"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p models data/input data/output data/sports

# Expose ports
EXPOSE 5000 8501 8765

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Entry point
ENTRYPOINT ["python", "skyjames.py"]
CMD ["--mode", "webcam"]
