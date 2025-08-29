FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy all requirements files
COPY requirements*.txt ./

# Install dependencies based on build argument
ARG BUILD_TYPE=api
RUN if [ "$BUILD_TYPE" = "streamlit" ] ; then \
        pip install --no-cache-dir -r requirements-streamlit.txt ; \
    else \
        pip install --no-cache-dir -r requirements.txt ; \
    fi

# Copy application files
COPY . .

# Expose ports (8000 for API, 8501 for Streamlit)
EXPOSE 8000 8501

# Run the appropriate service
CMD if [ "$BUILD_TYPE" = "streamlit" ] ; then \
        streamlit run streamlit_app.py --server.port=${PORT:-8501} --server.address=0.0.0.0 ; \
    else \
        uvicorn app-full:app --host 0.0.0.0 --port ${PORT:-8000} ; \
    fi