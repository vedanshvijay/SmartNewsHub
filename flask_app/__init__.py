from flask import Flask, session
from flask_caching import Cache
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv
import os
import pytz
from .news_service import NewsService
from .facts_service import FactsService
from .auth import login_manager

load_dotenv()

# Configure cache with more reliable settings
cache = Cache(config={
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_THRESHOLD': 1000
})

# Initialize scheduler with pytz timezone
scheduler = BackgroundScheduler(timezone=pytz.UTC)
news_service = NewsService()
facts_service = FactsService()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    
    # Initialize cache with app context
    cache.init_app(app)
    
    # Initialize login manager
    login_manager.init_app(app)
    
    # Register blueprints
    from .routes import main
    app.register_blueprint(main)
    
    # Schedule background tasks
    def update_news_cache():
        with app.app_context():
            try:
                # Update global and local news cache
                news = news_service.get_global_and_local_news()
                global_news = news['global_news']
                indian_news = news['indian_news']
                global_next_page = news['global_next']
                indian_next_page = news['indian_next']
                
                cache.set('global_news', global_news, timeout=1800)  # 30 minutes
                cache.set('indian_news', indian_news, timeout=1800)
                cache.set('global_next_page', global_next_page, timeout=1800)
                cache.set('indian_next_page', indian_next_page, timeout=1800)
                
                # Update category caches - categories that work with NewsData.io
                CATEGORIES = ['business', 'entertainment', 'health', 'science', 'sports', 'technology']
                for category in CATEGORIES:
                    category_news, next_page = news_service.get_headlines(category=category)
                    cache.set(f'category_{category}', category_news, timeout=1800)
                    cache.set(f'category_{category}_next_page', next_page, timeout=1800)
                
                # Update daily fact
                fact = facts_service.get_daily_fact()
                cache.set('daily_fact', fact, timeout=86400)  # 24 hours
            except Exception as e:
                print(f"Error updating cache: {str(e)}")
    
    # Add the job to the scheduler
    scheduler.add_job(
        func=update_news_cache,
        trigger=IntervalTrigger(minutes=30),
        id='update_news_cache',
        name='Update news cache every 30 minutes',
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    
    return app 