from newsapi import NewsApiClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class NewsService:
    def __init__(self):
        api_key = os.getenv('NEWS_API_KEY')
        print(f"Loading API key: {api_key[:5]}...")  # Print first 5 chars for security
        self.newsapi = NewsApiClient(api_key=api_key)

    def get_headlines(self, country='in', category=None, page_size=20):
        try:
            print(f"Fetching headlines for country: {country}, category: {category}")  # Debug log
            params = {
                'page_size': page_size
            }
            
            if country:
                params['country'] = country
            if category:
                params['category'] = category
            
            headlines = self.newsapi.get_top_headlines(**params)
            
            if headlines['status'] != 'ok':
                print(f"Error response: {headlines}")  # Print full error response
                return []

            formatted_articles = []
            for article in headlines['articles']:
                formatted_articles.append({
                    'title': article.get('title', 'Untitled Article'),
                    'description': article.get('description', ''),
                    'image_url': article.get('urlToImage'),
                    'source': article.get('source', {}).get('name', 'Unknown Source'),
                    'published_at': self._format_date(article.get('publishedAt')),
                    'url': article.get('url', '#')
                })
            
            print(f"Successfully fetched {len(formatted_articles)} articles")  # Debug log
            return formatted_articles
        except Exception as e:
            print(f"Error fetching headlines for {country}: {str(e)}")
            return []

    def get_indian_news(self, page_size=10):
        """Get Indian news using search instead of country filter"""
        try:
            print("Fetching Indian news via search...")
            # Search for news about India or from Indian sources
            news = self.newsapi.get_everything(
                q='India OR Indian',
                language='en',
                sort_by='publishedAt',
                page_size=page_size
            )
            
            if news['status'] != 'ok':
                print(f"Error response for Indian news search: {news}")
                return []

            formatted_articles = []
            for article in news['articles']:
                formatted_articles.append({
                    'title': article.get('title', 'Untitled Article'),
                    'description': article.get('description', ''),
                    'image_url': article.get('urlToImage'),
                    'source': article.get('source', {}).get('name', 'Unknown Source'),
                    'published_at': self._format_date(article.get('publishedAt')),
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
            date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
            return date.strftime('%B %d, %Y %I:%M %p')
        except Exception:
            return date_str

    def search_news(self, query, page_size=20):
        """Search news articles by keyword"""
        try:
            print(f"Searching news for query: {query}")
            news = self.newsapi.get_everything(
                q=query,
                language='en',
                sort_by='publishedAt',
                page_size=page_size
            )
            
            if news['status'] != 'ok':
                print(f"Error response for search query '{query}': {news}")
                return []

            formatted_articles = []
            for article in news['articles']:
                formatted_articles.append({
                    'title': article.get('title', 'Untitled Article'),
                    'description': article.get('description', ''),
                    'image_url': article.get('urlToImage'),
                    'source': article.get('source', {}).get('name', 'Unknown Source'),
                    'published_at': self._format_date(article.get('publishedAt')),
                    'url': article.get('url', '#')
                })
            
            print(f"Successfully fetched {len(formatted_articles)} articles for search query '{query}'")
            return formatted_articles
        except Exception as e:
            print(f"Error searching news: {str(e)}")
            return []
