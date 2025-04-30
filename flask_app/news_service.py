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

    def get_headlines(self, country=None, category=None, page_size=20):
        """Get top headlines, optionally by country or category"""
        try:
            print(f"Fetching headlines for country: {country}, category: {category}")  # Debug log
            
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
            
            response = requests.get(endpoint, params=params)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            data = response.json()
            
            if 'data' not in data:
                print(f"Error response: {data}")
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
            
            print(f"Successfully fetched {len(formatted_articles)} articles")  # Debug log
            return formatted_articles
        except Exception as e:
            print(f"Error fetching headlines for {country}: {str(e)}")
            return []

    def get_indian_news(self, page_size=10):
        """Get Indian news"""
        try:
            print("Fetching Indian news via search...")
            
            endpoint = f"{self.base_url}/all"
            
            params = {
                'api_token': self.api_key,
                'search': 'India OR Indian',
                'locale': 'in',
                'language': 'en',
                'limit': page_size
            }
            
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' not in data:
                print(f"Error response for Indian news search: {data}")
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
            
            print(f"Successfully fetched {len(formatted_articles)} Indian articles via search")
            return formatted_articles
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
