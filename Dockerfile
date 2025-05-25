# Use Python slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    libsndfile1-dev \
    ffmpeg \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create models directory
RUN mkdir -p models

# Copy application code
COPY main.py .
# COPY convert_to_onnx.py .

# Copy any pre-converted models (if available)
# COPY models/ models/ 2>/dev/null || :

# Set environment variables
# ENV MODEL_PATH=/app/models/stt_hi_conformer_ctc_medium.onnx
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Health check
# HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
#     CMD curl -f http://localhost:8000/health || exit 1

# Create a script to handle model conversion and startup
# RUN echo '#!/bin/bash\n\
# set -e\n\
# \n\
# # Check if ONNX model exists\n\
# if [ ! -f "$MODEL_PATH" ]; then\n\
#     echo "ONNX model not found. Converting from NeMo..."\n\
#     python convert_to_onnx.py\n\
# else\n\
#     echo "ONNX model found at $MODEL_PATH"\n\
# fi\n\
# \n\
# # Start the FastAPI server\n\
# exec uvicorn main:app --host 0.0.0.0 --port 8000\n\
# ' > /app/start.sh && chmod +x /app/start.sh

# Use script as entrypoint
CMD ["python","main.py"]