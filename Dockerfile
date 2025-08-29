FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for pandas/numpy
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-optimized.txt .
RUN pip install --no-cache-dir -r requirements-optimized.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app-full:app", "--host", "0.0.0.0", "--port", "8000"]