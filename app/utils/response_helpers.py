# app/utils/response_helpers.py
import math

def success_response(data=None, message=None, status_code=200):
    response = {'success': True}
    if data is not None:
        response['data'] = data
    if message:
        response['message'] = message
    return response, status_code

def error_response(message, code=None, details=None, status_code=400):
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

def paginated_response(items, page, per_page, total, endpoint=None):
    return {
        'success': True,
        'data': items,
        'pagination': {
            'page': page,
            'pages': math.ceil(total / per_page),
            'per_page': per_page,
            'total': total,
            'has_next': page * per_page < total,
            'has_prev': page > 1
        }
    }