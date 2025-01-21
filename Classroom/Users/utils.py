import hashlib

def generate_device_hash(request):
    """
    Generate a unique hash for the device using the user's IP address and user agent.
    """
    ip_address = request.META.get('REMOTE_ADDR', '')
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    combined_string = f"{ip_address}-{user_agent}"
    return hashlib.sha256(combined_string.encode()).hexdigest()