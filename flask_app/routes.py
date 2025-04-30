from flask import Blueprint, render_template, request, url_for, redirect, jsonify
from flask_app import cache, news_service, facts_service
from urllib.parse import quote_plus

main = Blueprint('main', __name__)

VALID_CATEGORIES = ['technology', 'business', 'sports', 'science', 'health', 'entertainment']

@main.route('/')
def index():
    # Try to get cached data first
    global_news = cache.get('global_news')
    indian_news = cache.get('indian_news')
    daily_fact = cache.get('daily_fact')
    
    # If cache is empty, fetch fresh data
    if not global_news or not indian_news:
        news = news_service.get_global_and_local_news()
        global_news = news['global_news']
        indian_news = news['indian_news']
        # Cache the fresh data
        cache.set('global_news', global_news, timeout=1800)
        cache.set('indian_news', indian_news, timeout=1800)
    
    # Get daily fact if not in cache
    if not daily_fact:
        daily_fact = facts_service.get_daily_fact()
        cache.set('daily_fact', daily_fact, timeout=86400)  # 24 hours
    
    return render_template('index.html', 
                         global_news=global_news,
                         indian_news=indian_news,
                         daily_fact=daily_fact,
                         categories=VALID_CATEGORIES)

@main.route('/category/<category_name>')
def category(category_name):
    # Normalize the category name
    category_name_lower = category_name.lower()
    
    # If someone uses dashes in the URL, convert to underscores
    category_name_normalized = category_name_lower.replace('-', '_')
    
    # If the URL doesn't match the normalized form, redirect to the correct URL
    if category_name != category_name_normalized and category_name_normalized.replace('_', '-') in VALID_CATEGORIES:
        return redirect(url_for('main.category', category_name=category_name_normalized.replace('_', '-')))
    
    if category_name_lower not in VALID_CATEGORIES:
        return render_template('error.html', 
                            message="Invalid category. Please choose from the available categories.",
                            categories=VALID_CATEGORIES)
    
    # Try to get cached data first
    articles = cache.get(f'category_{category_name_lower}')
    
    # If cache is empty, fetch fresh data
    if not articles:
        articles = news_service.get_headlines(category=category_name_lower, country=None, page_size=20)
        cache.set(f'category_{category_name_lower}', articles, timeout=1800)
    
    return render_template('category.html',
                         articles=articles,
                         category=category_name_lower,
                         categories=VALID_CATEGORIES)

@main.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return render_template('search.html', 
                             articles=[],
                             query='',
                             categories=VALID_CATEGORIES)
    
    # For search, we don't cache results as they are dynamic
    articles = news_service.search_news(query)
    
    # Create a clean, SEO-friendly URL for sharing
    clean_url = url_for('main.search', q=quote_plus(query), _external=True)
    
    return render_template('search.html',
                         articles=articles,
                         query=query,
                         clean_url=clean_url,
                         categories=VALID_CATEGORIES)

@main.route('/api/fact/random')
def random_fact():
    # Force a new fact by not using the cache
    fact = facts_service.get_daily_fact(force_new=True)
    return jsonify(fact) 