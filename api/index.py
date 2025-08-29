from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Redirect to Streamlit app with a fallback
        self.send_response(302)
        self.send_header('Location', 'https://tourism-analytics-platform-lenilani.streamlit.app/')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
        return
    
    def do_POST(self):
        self.do_GET()
        return