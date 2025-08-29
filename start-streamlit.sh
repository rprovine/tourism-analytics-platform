#!/bin/bash
# Start script for Streamlit on Render

# Set Streamlit configuration
export STREAMLIT_SERVER_PORT=${PORT:-8501}
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Run Streamlit
streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0