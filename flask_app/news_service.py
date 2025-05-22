"""
News Service Module for SmartNewsHub

This module handles all news-related operations including:
- Fetching news from external APIs
- Processing and analyzing news articles
- Managing article deduplication and similarity detection
- Handling API rate limits and fallbacks
"""

import requests  # HTTP library for making API requests
import os  # Operating system interface
import logging  # Logging facility for Python
from datetime import datetime  # Basic date and time types
from dotenv import load_dotenv  # Load environment variables from .env file
from urllib.parse import quote_plus  # URL encoding
from sklearn.feature_extraction.text import TfidfVectorizer  # Text feature extraction
from sklearn.metrics.pairwise import cosine_similarity  # Calculate text similarity
import numpy as np  # Numerical computing
from .ai_service import AIService  # AI analysis service
from .models import ArticleTags, db  # Database models

# Configure logging with timestamp and log level
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('news_service')

class NewsService:
    """
    Service class for handling news operations.
    
    This class manages:
    - API communication with news providers
    - Article processing and analysis
    - Content deduplication
    - Error handling and logging
    """
    
    def __init__(self):
        """
        Initialize the news service with API configuration and AI service.
        
        Sets up:
        - API keys and endpoints
        - Text processing tools
        - AI analysis service
        - Logging configuration
        """
        # Print current working directory and environment variables
        logger.info("Current working directory: %s", os.getcwd())
        logger.info("Environment variables: %s", list(os.environ.keys()))
        
        # Load environment variables from .env file
        env_path = os.path.join('/Applications/smartnewshub/SmartNewsHub', '.env')
        logger.info("Looking for .env file at: %s", env_path)
        if os.path.exists(env_path):
            logger.info(".env file found at: %s", env_path)
            load_dotenv(env_path)
        else:
            logger.error(".env file not found at: %s", env_path)
        
        # Initialize API configuration
        self.api_key = os.getenv('NEWSDATA_API_KEY')
        self.api_key_fallback = os.getenv('NEWSDATA_API_KEY_FALLBACK')
        self.base_url = "https://newsdata.io/api/1/news"
        self.default_language = 'en'
        self.similarity_threshold = 0.7  # Threshold for considering articles similar
        
        # Initialize text processing tools
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.ai_service = AIService()
        
        # Validate API key configuration
        if not self.api_key:
            logger.error("NEWSDATA_API_KEY not found in environment variables!")
            logger.error("Current environment variables: %s", list(os.environ.keys()))
            logger.error("Current working directory: %s", os.getcwd())
            logger.error("Please check that your .env file exists and contains NEWSDATA_API_KEY")
        else:
            logger.info("NewsData.io API key loaded successfully: %s...", self.api_key[:5])
            logger.info("API key length: %d", len(self.api_key))
            # Test API key with a simple request
            try:
                test_params = {'apikey': self.api_key, 'language': 'en', 'size': 1}
                test_response = requests.get(self.base_url, params=test_params)
                if test_response.status_code == 200:
                    logger.info("API key test successful")
                else:
                    logger.error("API key test failed with status code: %d", test_response.status_code)
                    logger.error("Response: %s", test_response.text)
            except Exception as e:
                logger.error("Error testing API key: %s", str(e))

    def _process_article_with_ai(self, article):
        """
        Process an article using AI analysis.
        
        Args:
            article (dict): Article data containing title and description
            
        Returns:
            ArticleTags: Database model instance with AI analysis results
        """
        try:
            # Combine title and description for analysis
            content = f"{article.get('title', '')} {article.get('description', '')}"
            
            # Get AI analysis results
            analysis = self.ai_service.analyze_article(content, article.get('title', ''))
            
            # Create or update article tags in database
            article_tags = ArticleTags.query.filter_by(article_id=article.get('article_id')).first()
            if not article_tags:
                article_tags = ArticleTags(article_id=article.get('article_id'))
            
            # Update tags with AI analysis results
            article_tags.tags = analysis.get('tags', [])
            article_tags.summary = analysis.get('summary', '')
            article_tags.sentiment = analysis.get('sentiment', {}).get('label', 'NEUTRAL')
            
            # Save to database
            db.session.add(article_tags)
            db.session.commit()
            
            return article_tags
        except Exception as e:
            logger.error(f"Error processing article with AI: {str(e)}")
            return None

    def _make_api_request(self, params):
        """
        Make API request with fallback key support.
        
        Args:
            params (dict): Request parameters
            
        Returns:
            Response: API response object or None if request fails
        """
        # Try with main API key
        params['apikey'] = self.api_key
        try:
            response = requests.get(self.base_url, params=params)
            if response.status_code == 200:
                return response
            logger.warning(f"Primary API key failed with status {response.status_code}. Trying fallback key if available.")
        except Exception as e:
            logger.warning(f"Primary API key request error: {e}. Trying fallback key if available.")
            
        # Try with fallback key if available
        if self.api_key_fallback:
            params['apikey'] = self.api_key_fallback
            try:
                response = requests.get(self.base_url, params=params)
                return response
            except Exception as e:
                logger.error(f"Fallback API key request error: {e}")
        return None

    def _detect_similar_content(self, articles):
        """
        Detect and remove articles with similar content using TF-IDF and cosine similarity.
        
        Args:
            articles (list): List of article dictionaries
            
        Returns:
            list: Filtered list of unique articles
        """
        if not articles:
            return articles

        # Combine title and description for better comparison
        texts = [f"{article['title']} {article['description']}" for article in articles]
        
        try:
            # Create TF-IDF matrix for text comparison
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Calculate cosine similarity between articles
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # Find and remove similar articles
            unique_articles = []
            seen_indices = set()
            
            for i in range(len(articles)):
                if i in seen_indices:
                    continue
                    
                unique_articles.append(articles[i])
                seen_indices.add(i)
                
                # Check similarity with remaining articles
                for j in range(i + 1, len(articles)):
                    if j in seen_indices:
                        continue
                        
                    if similarity_matrix[i, j] > self.similarity_threshold:
                        logger.info(f"Found similar articles: '{articles[i]['title']}' and '{articles[j]['title']}'")
                        seen_indices.add(j)
            
            logger.info(f"Removed {len(articles) - len(unique_articles)} similar articles")
            return unique_articles
            
        except Exception as e:
            logger.error(f"Error in content similarity detection: {str(e)}")
            return articles

    def get_headlines(self, page_size=10, page=0, category=None):
        """
        Fetch headlines from the news API.
        
        Args:
            page_size (int): Number of articles per page
            page (int/str): Page number or token
            category (str): News category filter
            
        Returns:
            tuple: (list of articles, next page token)
        """
        params = {
            'language': self.default_language,
            'size': page_size
        }
        
        # Add pagination and category parameters if provided
        if isinstance(page, str) and page:
            params['page'] = page
        if category:
            params['category'] = category
            
        try:
            logger.info(f"Fetching headlines with params: {params}")
            response = self._make_api_request(params)
            if not response:
                logger.error("No response from NewsData API (headlines)")
                return [], None
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') != 'success':
                logger.error(f"API Error response: {data}")
                return [], None
                
            next_page = data.get('nextPage')
            logger.info(f"Received next_page token: {next_page}")
            
            results = data.get('results', [])
            logger.info(f"Received {len(results)} articles from API")
            
            # Process and deduplicate articles
            seen_article_ids = set()
            articles = []
            
            for article in results:
                # Skip invalid articles
                if not article.get('description') or not article.get('link'):
                    continue
                
                # Create unique article ID
                article_id = article.get('article_id') or article.get('link')
                
                # Skip duplicates
                if article_id in seen_article_ids:
                    continue
                
                seen_article_ids.add(article_id)
                
                # Process article with AI
                article_tags = self._process_article_with_ai(article)
                    
                articles.append({
                    'title': article.get('title', 'Untitled Article'),
                    'description': article.get('description', 'No description available'),
                    'image_url': article.get('image_url'),
                    'source': article.get('source_id', 'Unknown Source'),
                    'published_at': self._format_date(article.get('pubDate')),
                    'url': article.get('link', '#'),
                    'id': article_id,
                    'summary': article_tags.summary if article_tags else None,
                    'sentiment': article_tags.sentiment if article_tags else None,
                    'tags': article_tags.tags if article_tags else []
                })
            
            # Remove similar content
            articles = self._detect_similar_content(articles)
            
            logger.info(f"Processed {len(articles)} valid articles after deduplication and similarity check")
            return articles, next_page
        except Exception as e:
            logger.error(f"Error fetching headlines: {str(e)}")
            return [], None

    def get_indian_news(self, page_size=10, page=0):
        # Use a different approach to get Indian news
        # Try adding a query for India-related content
        params = {
            'language': self.default_language,
            'q': 'India OR Delhi OR Mumbai',  # Search for India-related content
        }
        
        # Only add page parameter if it's not the first page
        if isinstance(page, str) and page:
            params['page'] = page
            
        try:
            logger.info(f"Fetching Indian news with params: {params}")
            response = self._make_api_request(params)
            if not response:
                logger.error("No response from NewsData API (indian news)")
                return [], None
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') != 'success':
                logger.error(f"API Error response for Indian news: {data}")
                return [], None
                
            next_page = data.get('nextPage')
            logger.info(f"Received next_page token for Indian news: {next_page}")
            
            results = data.get('results', [])
            logger.info(f"Received {len(results)} Indian news articles from API")
            
            articles = []
            for article in results:
                # Skip articles without descriptions or links
                if not article.get('description') or not article.get('link'):
                    continue
                
                # Create a unique article ID based on url or title
                article_id = article.get('article_id') or article.get('link')
                
                # Process article with AI
                article_tags = self._process_article_with_ai(article)
                    
                articles.append({
                    'title': article.get('title', 'Untitled Article'),
                    'description': article.get('description', 'No description available'),
                    'image_url': article.get('image_url'),
                    'source': article.get('source_id', 'Unknown Source'),
                    'published_at': self._format_date(article.get('pubDate')),
                    'url': article.get('link', '#'),
                    'id': article_id,
                    'summary': article_tags.summary if article_tags else None,
                    'sentiment': article_tags.sentiment if article_tags else None,
                    'tags': article_tags.tags if article_tags else []
                })
            
            # Remove similar content
            articles = self._detect_similar_content(articles)
            
            logger.info(f"Processed {len(articles)} valid Indian news articles after similarity check")
            return articles, next_page
        except Exception as e:
            logger.error(f"Error fetching Indian news: {str(e)}")
            return [], None

    def get_global_and_local_news(self):
        # Fetch global news - general headlines without any query
        global_news, global_next = self.get_headlines(page_size=5, page=0)
        logger.info(f"Fetched {len(global_news)} global news articles")
        
        # Fetch Indian news directly rather than using the nextPage from global news
        indian_news, indian_next = self.get_indian_news(page_size=5, page=0)
        logger.info(f"Fetched {len(indian_news)} Indian news articles")
        
        # Make sure there's no overlap between the two sets
        global_urls = {article['url'] for article in global_news}
        unique_indian_news = [article for article in indian_news if article['url'] not in global_urls]
        
        # Ensure equal number of articles
        min_articles = min(len(global_news), len(unique_indian_news))
        global_news = global_news[:min_articles]
        unique_indian_news = unique_indian_news[:min_articles]
        
        logger.info(f"After balancing: {len(global_news)} global news articles and {len(unique_indian_news)} Indian news articles")
        
        return {
            'global_news': global_news,
            'indian_news': unique_indian_news,
            'global_next': global_next,
            'indian_next': indian_next
        }

    def search_news(self, query, page=0):
        if not self.api_key:
            logger.error("Cannot perform search: API key is missing")
            return [], None
            
        params = {
            'language': self.default_language,
            'q': query,
            'size': 10,  # Changed from 20 to 10 to comply with API limits
            'category': None  # Allow all categories
        }
        
        # Only add page parameter if it's not the first page
        if isinstance(page, str) and page:
            params['page'] = page
            
        try:
            logger.info(f"Searching news with query: {query}, page: {page}")
            logger.info(f"Request URL: {self.base_url}")
            logger.info(f"Request params: {params}")
            
            response = self._make_api_request(params)
            if not response:
                logger.error("No response from NewsData API (search)")
                return [], None
            logger.info(f"Response status code: {response.status_code}")
            
            if response.status_code == 422:
                logger.error(f"API Error response: {response.text}")
                return [], None
                
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') != 'success':
                logger.error(f"API Error response: {data}")
                return [], None
                
            next_page = data.get('nextPage')
            logger.info(f"Received next_page token: {next_page}")
            
            results = data.get('results', [])
            logger.info(f"Received {len(results)} search results from API")
            
            # Get suggested corrections if available
            suggested_query = data.get('suggested_query')
            if suggested_query and suggested_query != query:
                logger.info(f"Suggested correction: {suggested_query}")
            
            articles = []
            seen_urls = set()  # Track seen URLs to prevent duplicates
            
            # Process main search results
            for article in results:
                # Skip articles without descriptions or links
                if not article.get('description') or not article.get('link'):
                    continue
                
                # Skip duplicates
                if article.get('link') in seen_urls:
                    continue
                seen_urls.add(article.get('link'))
                
                # Create a unique article ID based on url or title
                article_id = article.get('article_id') or article.get('link')
                
                # Process article with AI
                article_tags = self._process_article_with_ai(article)
                    
                articles.append({
                    'title': article.get('title', 'Untitled Article'),
                    'description': article.get('description', 'No description available'),
                    'image_url': article.get('image_url'),
                    'source': article.get('source_id', 'Unknown Source'),
                    'published_at': self._format_date(article.get('pubDate')),
                    'url': article.get('link', '#'),
                    'id': article_id,
                    'summary': article_tags.summary if article_tags else None,
                    'sentiment': article_tags.sentiment if article_tags else None,
                    'tags': article_tags.tags if article_tags else []
                })
            
            # If we have suggested corrections, add them to the response
            if suggested_query:
                articles.append({
                    'title': f'Did you mean "{suggested_query}"?',
                    'description': f'We found more results for "{suggested_query}". Click to search with this term.',
                    'url': f'/search?q={quote_plus(suggested_query)}',
                    'is_suggestion': True
                })
            
            # Remove similar content
            articles = self._detect_similar_content(articles)
            
            logger.info(f"Returning {len(articles)} processed articles")
            return articles, next_page
            
        except Exception as e:
            logger.error(f"Error in search_news: {str(e)}")
            return [], None

    def get_local_news(self, country=None, city=None, state=None):
        """Fetch local news based on country, state, and city"""
        try:
            # Build query parameters
            params = {
                'language': 'en',
                'size': 10  # Set equal limit for all news types
            }
            
            # Add location parameters if provided
            if country:
                params['country'] = country
            if state:
                params['q'] = f"{state} OR {city}" if city else state
            elif city:
                params['q'] = city
            
            # Make API request
            response = self._make_api_request(params)
            if not response:
                logger.error("No response from NewsData API (local news)")
                return []
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            if data.get('status') == 'success':
                articles = data.get('results', [])
                processed_articles = []
                
                for article in articles:
                    # Process article with AI
                    article_tags = self._process_article_with_ai(article)
                    
                    processed_articles.append({
                        'title': article.get('title', 'Untitled Article'),
                        'description': article.get('description', 'No description available'),
                        'image_url': article.get('image_url'),
                        'source': article.get('source_id', 'Unknown Source'),
                        'published_at': self._format_date(article.get('pubDate')),
                        'url': article.get('link', '#'),
                        'id': article.get('article_id') or article.get('link'),
                        'summary': article_tags.summary if article_tags else None,
                        'sentiment': article_tags.sentiment if article_tags else None,
                        'tags': article_tags.tags if article_tags else []
                    })
                
                return processed_articles
            else:
                logger.error(f"Error fetching local news: {data.get('message', 'Unknown error')}")
                return []
                
        except Exception as e:
            logger.error(f"Error in get_local_news: {str(e)}")
            return []

    def _format_date(self, date_str):
        """
        Format date string into a readable format.
        
        Args:
            date_str (str): Date string in format 'YYYY-MM-DD HH:MM:SS'
            
        Returns:
            str: Formatted date string or original if parsing fails
        """
        if not date_str:
            return None
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            return date.strftime('%B %d, %Y %I:%M %p')
        except Exception:
            return date_str

    def get_breaking_news(self):
        """Get breaking news articles."""
        try:
            params = {
                'language': 'en',
                'size': 5,
                'category': 'top',
                'live': True  # Enable live news feature
            }
            
            response = self._make_api_request(params)
            if not response:
                logger.error("No response from NewsData API (breaking news)")
                return []
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'success':
                articles = []
                for article in data.get('results', []):
                    if article.get('title') and article.get('link'):
                        # Process article with AI
                        article_tags = self._process_article_with_ai(article)
                        
                        articles.append({
                            'title': article['title'],
                            'url': article['link'],
                            'source': article.get('source_id', 'Unknown'),
                            'published_at': article.get('pubDate', 'N/A'),
                            'summary': article_tags.summary if article_tags else None,
                            'sentiment': article_tags.sentiment if article_tags else None,
                            'tags': article_tags.tags if article_tags else []
                        })
                return articles
            return []
            
        except Exception as e:
            logger.error(f"Error in get_breaking_news: {str(e)}")
            return []
