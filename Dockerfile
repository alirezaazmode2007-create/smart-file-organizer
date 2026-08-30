# Smart File Organizer - Docker Image
# Multi-stage build for smaller final image

# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml README.md ./
COPY smart_file_organizer/ ./smart_file_organizer/
COPY config/ ./config/
COPY FILE_CATEGORIES.json ./

# Install package in development mode
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -e .

# Runtime stage
FROM python:3.12-slim AS runtime

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy installed package from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application files
COPY --from=builder /app/smart_file_organizer ./smart_file_organizer
COPY --from=builder /app/config ./config
COPY --from=builder /app/FILE_CATEGORIES.json ./

# Create data directory for volume mounting
RUN mkdir -p /data && chown -R appuser:appuser /app /data

# Switch to non-root user
USER appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/usr/local/bin:${PATH}"

# Default command
ENTRYPOINT ["smart-file-organizer"]

# Allow passing directory as argument
CMD ["/data"]