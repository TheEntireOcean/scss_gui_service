from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from app.utils.response_helpers import error_response
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """Register all error handlers"""
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        logger.warning(f"Validation error: {e.messages}")
        return error_response(
            message="Validation error",
            code="VALIDATION_ERROR",
            details=e.messages,
            status_code=400
        )
    
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(e):
        logger.error(f"Database integrity error: {str(e)}")
        if 'unique constraint' in str(e).lower():
            return error_response(
                message="Resource already exists",
                code="DUPLICATE_RESOURCE",
                status_code=409
            )
        return error_response(
            message="Database error occurred",
            code="DATABASE_ERROR",
            status_code=500
        )
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        response = {
            'success': False,
            'error': {
                'message': e.description,
                'code': e.name.upper().replace(' ', '_')
            }
        }
        return jsonify(response), e.code
    
    @app.errorhandler(404)
    def handle_not_found(e):
        return error_response(
            message="Resource not found",
            code="NOT_FOUND",
            status_code=404
        )
    
    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        return error_response(
            message="Method not allowed",
            code="METHOD_NOT_ALLOWED",
            status_code=405
        )
    
    @app.errorhandler(500)
    def handle_internal_server_error(e):
        logger.error(f"Internal server error: {str(e)}")
        return error_response(
            message="Internal server error",
            code="INTERNAL_SERVER_ERROR",
            status_code=500
        )
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        logger.error(f"Unexpected error: {str(e)}")
        return error_response(
            message="An unexpected error occurred",
            code="UNEXPECTED_ERROR",
            status_code=500
        )