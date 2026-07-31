"""
ARUA AI - WSGI Entry Point
For production deployment with Gunicorn
Usage: gunicorn wsgi:app
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run()
