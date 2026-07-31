"""
AURA AI - Main Flask Application
Production-ready AI Creative Platform Backend
"""

import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory pattern for production-ready Flask app."""
    app = Flask(__name__)
    
    # Security configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'arua-ai-secret-key-change-in-production')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    
    # CORS configuration - restrict to frontend origin in production
    CORS(app, resources={
        r"/api/*": {
            "origins": os.getenv('ALLOWED_ORIGINS', '*').split(','),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
        }
    })
    
    # Register blueprints
    from api.auth import auth_bp
    from api.generate import generate_bp
    from api.gallery import gallery_bp
    from api.profile import profile_bp
    from api.admin import admin_bp
    from api.collections import collections_bp
    from api.editor import editor_bp
    from api.projects import projects_bp
    from api.watson import watson_bp
    from api.video import video_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(generate_bp, url_prefix='/api')
    app.register_blueprint(gallery_bp, url_prefix='/api')
    app.register_blueprint(profile_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api')
    app.register_blueprint(collections_bp, url_prefix='/api')
    app.register_blueprint(editor_bp, url_prefix='/api')
    app.register_blueprint(projects_bp, url_prefix='/api')
    app.register_blueprint(watson_bp, url_prefix='/api')
    app.register_blueprint(video_bp, url_prefix='/api')
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'version': '1.0.0',
            'service': 'AURA AI Backend'
        }), 200
    
    # Global error handlers
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'error': 'Bad request', 'message': str(e)}), 400
    
    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401
    
    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({'error': 'Forbidden', 'message': 'Access denied'}), 403
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404
    
    @app.errorhandler(429)
    def rate_limited(e):
        return jsonify({'error': 'Rate limited', 'message': 'Too many requests'}), 429
    
    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Internal server error: {e}")
        return jsonify({'error': 'Internal server error', 'message': 'Something went wrong'}), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'production') == 'development'
    
    logger.info(f"Starting AURA AI Backend on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
