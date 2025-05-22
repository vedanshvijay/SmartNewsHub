"""
Sitemap Generator for PlanetPulse

This module generates a sitemap.xml file for better SEO indexing.
"""

from flask import Blueprint, make_response
from datetime import datetime
import xml.etree.ElementTree as ET
from . import db
from .models import Article

sitemap = Blueprint('sitemap', __name__)

@sitemap.route('/sitemap.xml')
def generate_sitemap():
    """Generate sitemap.xml for search engines."""
    # Create the root element
    urlset = ET.Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    
    # Add static pages
    static_pages = [
        {'loc': '/', 'changefreq': 'daily', 'priority': '1.0'},
        {'loc': '/about', 'changefreq': 'monthly', 'priority': '0.8'},
        {'loc': '/contact', 'changefreq': 'monthly', 'priority': '0.8'},
        {'loc': '/privacy-policy', 'changefreq': 'monthly', 'priority': '0.5'},
        {'loc': '/terms', 'changefreq': 'monthly', 'priority': '0.5'},
    ]
    
    # Add category pages
    categories = [
        'business', 'technology', 'sports', 'entertainment',
        'health', 'science', 'education', 'politics'
    ]
    
    for category in categories:
        static_pages.append({
            'loc': f'/category/{category}',
            'changefreq': 'daily',
            'priority': '0.9'
        })
    
    # Add static pages to sitemap
    for page in static_pages:
        url = ET.SubElement(urlset, 'url')
        ET.SubElement(url, 'loc').text = f'https://planetpulse.com{page["loc"]}'
        ET.SubElement(url, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
        ET.SubElement(url, 'changefreq').text = page['changefreq']
        ET.SubElement(url, 'priority').text = page['priority']
    
    # Add dynamic article pages
    articles = Article.query.all()
    for article in articles:
        url = ET.SubElement(urlset, 'url')
        ET.SubElement(url, 'loc').text = f'https://planetpulse.com/article/{article.id}'
        ET.SubElement(url, 'lastmod').text = article.updated_at.strftime('%Y-%m-%d')
        ET.SubElement(url, 'changefreq').text = 'weekly'
        ET.SubElement(url, 'priority').text = '0.7'
    
    # Create the XML string
    sitemap_xml = ET.tostring(urlset, encoding='unicode', method='xml')
    
    # Create the response
    response = make_response(sitemap_xml)
    response.headers['Content-Type'] = 'application/xml'
    
    return response 