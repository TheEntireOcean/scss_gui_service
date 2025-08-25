# gui-service/app/utils/validators.py

# Placeholder for validators
def validate_camera_source(source):
    # Implement regex validation as per security section
    import re
    pattern = r'^(rtsp://|http://|/dev/)'
    return bool(re.match(pattern, source))