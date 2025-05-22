"""
Image Optimization Utility for PlanetPulse

This module provides functions for optimizing images and ensuring proper alt tags.
"""

import os
from PIL import Image
import requests
from io import BytesIO
from flask import current_app
import hashlib

def optimize_image(image_url, alt_text=None):
    """
    Optimize an image and ensure it has proper alt text.
    
    Args:
        image_url (str): URL of the image to optimize
        alt_text (str): Alt text for the image
        
    Returns:
        dict: Dictionary containing optimized image URL and alt text
    """
    try:
        # Generate a hash for the image URL
        image_hash = hashlib.md5(image_url.encode()).hexdigest()
        
        # Check if image is already cached
        cache_dir = os.path.join(current_app.static_folder, 'cache', 'images')
        os.makedirs(cache_dir, exist_ok=True)
        
        cached_path = os.path.join(cache_dir, f"{image_hash}.jpg")
        
        if not os.path.exists(cached_path):
            # Download and optimize image
            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content))
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Resize if too large
            max_size = (1200, 1200)
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.LANCZOS)
            
            # Save optimized image
            img.save(cached_path, 'JPEG', quality=85, optimize=True)
        
        # Generate alt text if not provided
        if not alt_text:
            alt_text = f"News image from {image_url.split('/')[-1]}"
        
        return {
            'url': f"/static/cache/images/{image_hash}.jpg",
            'alt': alt_text
        }
        
    except Exception as e:
        current_app.logger.error(f"Error optimizing image: {str(e)}")
        return {
            'url': image_url,
            'alt': alt_text or 'News image'
        }

def get_image_metadata(image_path):
    """
    Get metadata for an image.
    
    Args:
        image_path (str): Path to the image
        
    Returns:
        dict: Image metadata
    """
    try:
        with Image.open(image_path) as img:
            return {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode
            }
    except Exception as e:
        current_app.logger.error(f"Error getting image metadata: {str(e)}")
        return {} 