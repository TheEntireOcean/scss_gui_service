# app/api/middleware/error_handlers.py
from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import NotFound, Unauthorized, Forbidden

def register_error_handlers(app):
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid input data',
                'details': e.messages
            }
        }), 400
    
    @app.errorhandler(NotFound)
    def handle_not_found(e):
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Resource not found'
            }
        }), 404
    
    @app.errorhandler(Unauthorized)
    def handle_unauthorized(e):
        return jsonify({
            'success': False,
            'error': {
                'code': 'UNAUTHORIZED',
                'message': 'Authentication required'
            }
        }), 401
    
    @app.errorhandler(Forbidden)
    def handle_forbidden(e):
        return jsonify({
            'success': False,
            'error': {
                'code': 'FORBIDDEN',
                'message': 'Access denied'
            }
        }), 403
    
    @app.errorhandler(500)
    def handle_internal_server_error(e):
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An unexpected error occurred'
            }
        }), 500