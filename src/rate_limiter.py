from flask import request, jsonify
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests=100, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_ip):
        now = time.time()
        self.requests[client_ip] = [req for req in self.requests[client_ip] if req > now - self.time_window]
        if len(self.requests[client_ip]) >= self.max_requests:
            return False
        self.requests[client_ip].append(now)
        return True

def rate_limit(f):
    def wrapper(*args, **kwargs):
        client_ip = request.remote_addr
        limiter = RateLimiter()
        if not limiter.is_allowed(client_ip):
            return jsonify({'error': 'Rate limit exceeded'}), 429
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper
