import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class NewsService:
    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY')
        self.base_url = "https://api.thenewsapi.com/v1/news"
        print(f"Loading API key: {self.api_key[:5]}...")  # Print first 5 chars for security
        # Store already fetched articles to avoid duplicates
        self.cached_articles = {
            'global': [],
            'indian': []
        }

    def get_headlines(self, country=None, category=None, page_size=20, page=1):
        """Get top headlines, optionally by country or category"""
        try:
            print(f"Fetching headlines for country: {country}, category: {category}, page: {page}")
            
            # For TheNewsAPI, we'll use the top_stories endpoint
            endpoint = f"{self.base_url}/top"
            
            params = {
                'api_token': self.api_key,
                'limit': page_size
            }
            
            # Map categories to TheNewsAPI format if needed
            if category:
                params['categories'] = category
            
            # Map country to locale in TheNewsAPI
            if country:
                params['locale'] = country
                
            # If page > 1, we need to fetch new articles that haven't been seen before
            # Since TheNewsAPI doesn't support direct pagination, we'll increase the limit
            # and then filter out already seen articles
            if page > 1:
                # Increase the fetch count to get more articles
                params['limit'] = page_size * 2
                
            response = requests.get(endpoint, params=params)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            data = response.json()
            
            if 'data' not in data:
                print(f"Error response: {data}")
                return []

            all_articles = data.get('data', [])
            formatted_articles = []
            
            # Create a set of already seen article URLs for easy lookup
            cached_urls = {article['url'] for article in self.cached_articles['global']}
            
            # Process new articles
            new_articles = []
            for article in all_articles:
                # Skip if we've already processed this article
                if article.get('url') in cached_urls:
                    continue
                    
                formatted_article = {
                    'title': article.get('title', 'Untitled Article'),
                    'description': article.get('description', 'No description available'),
                    'image_url': article.get('image_url'),
                    'source': article.get('source', 'Unknown Source'),
                    'published_at': self._format_date(article.get('published_at')),
                    'url': article.get('url', '#')
                }
                
                new_articles.append(formatted_article)
                cached_urls.add(article.get('url', '#'))
                
                if len(new_articles) >= page_size:
                    break
            
            # Update our cache with new articles
            self.cached_articles['global'].extend(new_articles)
            
            print(f"Successfully fetched {len(new_articles)} new articles")
            return new_articles
        except Exception as e:
            print(f"Error fetching headlines for {country}: {str(e)}")
            return []

    def get_indian_news(self, page_size=10, page=1):
        """Get Indian news"""
        try:
            print(f"Fetching Indian news via search... page: {page}")
            
            endpoint = f"{self.base_url}/all"
            
            params = {
                'api_token': self.api_key,
                'search': 'India OR Indian',
                'locale': 'in',
                'language': 'en',
                'limit': page_size
            }
            
            # If page > 1, fetch more articles to find new ones
            if page > 1:
                params['limit'] = page_size * 2
            
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' not in data:
                print(f"Error response for Indian news search: {data}")
                return []

            all_articles = data.get('data', [])
            
            # Create a set of already seen article URLs for easy lookup
            cached_urls = {article['url'] for article in self.cached_articles['indian']}
            
            # Process new articles
            new_articles = []
            for article in all_articles:
                # Skip if we've already processed this article
                if article.get('url') in cached_urls:
                    continue
                
                formatted_article = {
                    'title': article.get('title', 'Untitled Article'),
                    'description': article.get('description', 'No description available'),
                    'image_url': article.get('image_url'),
                    'source': article.get('source', 'Unknown Source'),
                    'published_at': self._format_date(article.get('published_at')),
                    'url': article.get('url', '#')
                }
                
                new_articles.append(formatted_article)
                cached_urls.add(article.get('url', '#'))
                
                if len(new_articles) >= page_size:
                    break
            
            # Update our cache with new articles
            self.cached_articles['indian'].extend(new_articles)
            
            print(f"Successfully fetched {len(new_articles)} new Indian articles")
            return new_articles
        except Exception as e:
            print(f"Error fetching Indian news: {str(e)}")
            return []

    def get_global_and_local_news(self):
        """Fetch both global and Indian news"""
        print("Fetching global news...")
        global_news = self.get_headlines(country='us', page_size=10)
        print("Fetching Indian news...")
        indian_news = self.get_indian_news(page_size=10)
        
        return {
            'global_news': global_news,
            'indian_news': indian_news
        }

    def _format_date(self, date_str):
        """Format the date string to a more readable format"""
        if not date_str:
            return None
        try:
            date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
            return date.strftime('%B %d, %Y %I:%M %p')
        except Exception:
            try:
                # Try another format if the first one fails
                date = datetime.strptime(date_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')
                return date.strftime('%B %d, %Y %I:%M %p')
            except Exception:
                return date_str

    def search_news(self, query, page_size=20):
        """Search news articles by keyword"""
        try:
            print(f"Searching news for query: {query}")
            
            endpoint = f"{self.base_url}/all"
            
            params = {
                'api_token': self.api_key,
                'search': query,
                'language': 'en',
                'limit': page_size
            }
            
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' not in data:
                print(f"Error response for search query '{query}': {data}")
                return []

            formatted_articles = []
            for article in data.get('data', []):
                formatted_articles.append({
                    'title': article.get('title', 'Untitled Article'),
                    'description': article.get('description', 'No description available'),
                    'image_url': article.get('image_url'),
                    'source': article.get('source', 'Unknown Source'),
                    'published_at': self._format_date(article.get('published_at')),
                    'url': article.get('url', '#')
                })
            
            print(f"Successfully fetched {len(formatted_articles)} articles for search query '{query}'")
            return formatted_articles
        except Exception as e:
            print(f"Error searching news: {str(e)}")
            return []
