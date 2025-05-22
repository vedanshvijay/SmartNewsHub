"""
Performance Optimization Utility for PlanetPulse

This module provides functions for optimizing page load performance.
"""

from flask import request, g
import time
from functools import wraps
import re

def minify_html(html):
    """
    Minify HTML content.
    
    Args:
        html (str): HTML content to minify
        
    Returns:
        str: Minified HTML
    """
    # Remove comments
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    
    # Remove whitespace between tags
    html = re.sub(r'>\s+<', '><', html)
    
    # Remove whitespace at the start and end
    html = html.strip()
    
    return html

def performance_monitor(f):
    """
    Decorator to monitor route performance.
    
    Args:
        f: Function to decorate
        
    Returns:
        function: Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Start timer
        g.start_time = time.time()
        
        # Call the function
        response = f(*args, **kwargs)
        
        # Calculate execution time
        execution_time = time.time() - g.start_time
        
        # Add performance header
        if isinstance(response, str):
            response = minify_html(response)
        
        return response
    return decorated_function

def add_performance_headers(response):
    """
    Add performance-related headers to the response.
    
    Args:
        response: Flask response object
        
    Returns:
        response: Modified response object
    """
    # Add security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Add cache control headers
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=31536000'
    else:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    
    return response

def optimize_static_urls(url):
    """
    Optimize static URLs for better caching.
    
    Args:
        url (str): URL to optimize
        
    Returns:
        str: Optimized URL
    """
    if url.startswith('/static/'):
        # Add version parameter for cache busting
        version = int(time.time())
        separator = '&' if '?' in url else '?'
        return f"{url}{separator}v={version}"
    return url 