# Face Recognition System v1.2.0 - Production Docker Image
# Enhanced with improved face_recognition API and user experience
# Multi-stage build for optimized image size

# Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    APP_VERSION=v1.2.0

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    python3-dev \
    git \
    pkg-config \
    libdlib-dev \
    libboost-all-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies in stages
COPY config/requirements-base.txt /tmp/requirements-base.txt
COPY config/requirements-heavy.txt /tmp/requirements-heavy.txt

# Install base packages first (fast)
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /tmp/requirements-base.txt

# Install heavy packages with extended timeout (including face_recognition)
RUN pip install --no-cache-dir --timeout 1800 -r /tmp/requirements-heavy.txt

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    FACE_RECOGNITION_ENV=production \
    APP_VERSION=v1.2.0

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgtk-3-0 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxext6 \
    libsm6 \
    libxrender1 \
    libfontconfig1 \
    libice6 \
    libopenblas-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create non-root user for security
RUN groupadd -r faceapp && useradd -r -g faceapp faceapp

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=faceapp:faceapp . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/data/face_encodings /app/static/uploads && \
    chown -R faceapp:faceapp /app

# Switch to non-root user
USER faceapp

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Default command
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"] 