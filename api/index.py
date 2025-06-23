"""
Vercel serverless function entry point
"""
from main import app

# Vercel requires the app to be available at this path
handler = app