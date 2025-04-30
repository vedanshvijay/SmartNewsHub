import requests
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('news_service')

class NewsService:
    def __init__(self):
        self.api_key = os.getenv('NEWSDATA_API_KEY')
        self.base_url = "https://newsdata.io/api/1/news"
        self.default_language = 'en'
        if self.api_key:
            logger.info(f"NewsData.io API key loaded: {self.api_key[:5]}...")
        else:
            logger.warning("NEWSDATA_API_KEY not found in environment variables")

    def get_headlines(self, page_size=10, page=0, category=None):
        params = {
            'apikey': self.api_key,
            'language': self.default_language,
        }
        
        # Only add page parameter if it's not the first page (NewsData.io uses nextPage token)
        if isinstance(page, str) and page:
            params['page'] = page
            
        # Only add category if specified and not None
        if category:
            params['category'] = category
            
        try:
            logger.info(f"Fetching headlines with params: {params}")
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') != 'success':
                logger.error(f"API Error response: {data}")
                return [], None
                
            next_page = data.get('nextPage')
            logger.info(f"Received next_page token: {next_page}")
            
            results = data.get('results', [])
            logger.info(f"Received {len(results)} articles from API")
            
            articles = []
            for article in results:
                # Skip articles without descriptions or links
                if not article.get('description') or not article.get('link'):
                    continue
                
                # Create a unique article ID based on url or title
                article_id = article.get('article_id') or article.get('link')
                    
                articles.append({
                    'title': article.get('title', 'Untitled Article'),
                    'description': article.get('description', 'No description available'),
                    'image_url': article.get('image_url'),
                    'source': article.get('source_id', 'Unknown Source'),
                    'published_at': self._format_date(article.get('pubDate')),
                    'url': article.get('link', '#'),
                    'id': article_id  # Add unique ID for deduplication
                })
            
            logger.info(f"Processed {len(articles)} valid articles")
            return articles, next_page
        except Exception as e:
            logger.error(f"Error fetching headlines: {str(e)}")
            return [], None

    def get_indian_news(self, page_size=10, page=0):
        # Use a different approach to get Indian news
        # Try adding a query for India-related content
        params = {
            'apikey': self.api_key,
            'language': self.default_language,
            'q': 'India OR Delhi OR Mumbai',  # Search for India-related content
        }
        
        # Only add page parameter if it's not the first page
        if isinstance(page, str) and page:
            params['page'] = page
            
        try:
            logger.info(f"Fetching Indian news with params: {params}")
            response = requests.get(self.base_url, params=params)
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
                    
                articles.append({
                    'title': article.get('title', 'Untitled Article'),
                    'description': article.get('description', 'No description available'),
                    'image_url': article.get('image_url'),
                    'source': article.get('source_id', 'Unknown Source'),
                    'published_at': self._format_date(article.get('pubDate')),
                    'url': article.get('link', '#'),
                    'id': article_id  # Add unique ID for deduplication
                })
            
            logger.info(f"Processed {len(articles)} valid Indian news articles")
            return articles, next_page
        except Exception as e:
            logger.error(f"Error fetching Indian news: {str(e)}")
            return [], None

    def get_global_and_local_news(self):
        # Fetch global news - general headlines without any query
        global_news, global_next = self.get_headlines(page_size=6, page=0)
        logger.info(f"Fetched {len(global_news)} global news articles")
        
        # Fetch Indian news directly rather than using the nextPage from global news
        indian_news, indian_next = self.get_indian_news(page_size=6, page=0)
        logger.info(f"Fetched {len(indian_news)} Indian news articles")
        
        # Make sure there's no overlap between the two sets
        global_urls = {article['url'] for article in global_news}
        unique_indian_news = [article for article in indian_news if article['url'] not in global_urls]
        
        logger.info(f"After deduplication: {len(unique_indian_news)} unique Indian news articles")
        
        return {
            'global_news': global_news,
            'indian_news': unique_indian_news,
            'global_next': global_next,
            'indian_next': indian_next
        }

    def search_news(self, query, page=0):
        params = {
            'apikey': self.api_key,
            'language': self.default_language,
            'q': query,
        }
        
        # Only add page parameter if it's not the first page
        if isinstance(page, str) and page:
            params['page'] = page
            
        try:
            logger.info(f"Searching news with query: {query}, page: {page}")
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') != 'success':
                logger.error(f"API Error response: {data}")
                return [], None
                
            next_page = data.get('nextPage')
            logger.info(f"Received next_page token: {next_page}")
            
            results = data.get('results', [])
            logger.info(f"Received {len(results)} search results from API")
            
            articles = []
            for article in results:
                # Skip articles without descriptions or links
                if not article.get('description') or not article.get('link'):
                    continue
                
                # Create a unique article ID based on url or title
                article_id = article.get('article_id') or article.get('link')
                    
                articles.append({
                    'title': article.get('title', 'Untitled Article'),
                    'description': article.get('description', 'No description available'),
                    'image_url': article.get('image_url'),
                    'source': article.get('source_id', 'Unknown Source'),
                    'published_at': self._format_date(article.get('pubDate')),
                    'url': article.get('link', '#'),
                    'id': article_id  # Add unique ID for deduplication
                })
            
            logger.info(f"Processed {len(articles)} valid search results")
            return articles, next_page
        except Exception as e:
            logger.error(f"Error searching news: {str(e)}")
            return [], None

    def _format_date(self, date_str):
        if not date_str:
            return None
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            return date.strftime('%B %d, %Y %I:%M %p')
        except Exception:
            return date_str
