FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TORCH_HOME=/app/.torch

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install torch with pre-built wheels (CPU-only for smaller size)
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install other dependencies
RUN pip install --no-cache-dir \
    fastapi>=0.100.0 \
    uvicorn[standard]>=0.23.0 \
    jinja2>=3.1.0 \
    python-multipart>=0.0.6 \
    sentence-transformers>=2.2.0 \
    plotly>=5.17.0 \
    pandas>=2.0.0 \
    numpy>=1.24.0 \
    scikit-learn>=1.3.0 \
    xgboost>=2.0.0 \
    shap>=0.42.0 \
    python-Levenshtein>=0.21.0 \
    reportlab>=4.0.0 \
    pydantic>=2.0.0

# Copy application code after dependencies (expensive layer is cached)
COPY . .

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
