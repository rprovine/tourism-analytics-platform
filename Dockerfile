FROM python:3.11-slim

WORKDIR /app

# Copy and install requirements (using minimal requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit app
CMD streamlit run streamlit_app.py --server.port=${PORT:-8501} --server.address=0.0.0.0