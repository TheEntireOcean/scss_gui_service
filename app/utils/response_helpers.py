import math
from flask import url_for, request

def success_response(data=None, message=None, status_code=200):
    """Create a successful response"""
    response = {'success': True}
    if data is not None:
        response['data'] = data
    if message:
        response['message'] = message
    return response, status_code

def error_response(message, code=None, details=None, status_code=400):
    """Create an error response"""
    response = {
        'success': False,
        'error': {
            'message': message
        }
    }
    if code:
        response['error']['code'] = code
    if details:
        response['error']['details'] = details
    return response, status_code

def paginated_response(items, page, per_page, total, endpoint=None, **kwargs):
    """Create a paginated response"""
    return {
        'success': True,
        'data': items,
        'pagination': {
            'page': page,
            'pages': math.ceil(total / per_page) if per_page > 0 else 1,
            'per_page': per_page,
            'total': total,
            'has_next': page * per_page < total,
            'has_prev': page > 1,
            'next_url': url_for(endpoint, page=page + 1, per_page=per_page, **kwargs) if endpoint and page * per_page < total else None,
            'prev_url': url_for(endpoint, page=page - 1, per_page=per_page, **kwargs) if endpoint and page > 1 else None
        }
    }

def validation_error_response(errors, status_code=400):
    """Create a validation error response"""
    return error_response(
        message="Validation error",
        code="VALIDATION_ERROR",
        details=errors,
        status_code=status_code
    )