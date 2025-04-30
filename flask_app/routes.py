from flask import Blueprint, render_template, request, url_for, redirect, jsonify, session, flash, current_app
from flask_app import cache, news_service, facts_service
from urllib.parse import quote_plus
import os

main = Blueprint('main', __name__)

# Update categories to match NewsData.io categories
VALID_CATEGORIES = ['top', 'world', 'business', 'entertainment', 'health', 'science', 'sports', 'technology', 'politics']

# Dictionary to store the article IDs we've already shown to avoid duplication
SHOWN_ARTICLES = {
    'global': set(),
    'indian': set(),
}

@main.route('/')
def index():
    # Try to get cached data first
    global_news = cache.get('global_news')
    indian_news = cache.get('indian_news')
    daily_fact = cache.get('daily_fact')
    global_next_page = cache.get('global_next_page')
    indian_next_page = cache.get('indian_next_page')
    
    # Initialize or clear the shown articles for a new session
    session.pop('shown_global_articles', None)
    session.pop('shown_indian_articles', None)
    
    # If cache is empty, fetch fresh data
    if not global_news or not indian_news:
        news = news_service.get_global_and_local_news()
        global_news = news['global_news']
        indian_news = news['indian_news']
        global_next_page = news['global_next']
        indian_next_page = news['indian_next']
        
        # Cache the fresh data
        cache.set('global_news', global_news, timeout=1800)
        cache.set('indian_news', indian_news, timeout=1800)
        cache.set('global_next_page', global_next_page, timeout=1800)
        cache.set('indian_next_page', indian_next_page, timeout=1800)
    
    # Get daily fact if not in cache
    if not daily_fact:
        daily_fact = facts_service.get_daily_fact()
        cache.set('daily_fact', daily_fact, timeout=86400)  # 24 hours
    
    # Store next page tokens in session for load more functionality
    session['global_next_page'] = global_next_page
    session['indian_next_page'] = indian_next_page
    
    # Track which articles we've shown to avoid duplication
    session['shown_global_articles'] = [article['url'] for article in global_news]
    session['shown_indian_articles'] = [article['url'] for article in indian_news]
    
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
    cache_key = f'category_{category_name_lower}'
    articles = cache.get(cache_key)
    next_page = cache.get(f'{cache_key}_next_page')
    
    # If cache is empty, fetch fresh data
    if not articles:
        articles, next_page = news_service.get_headlines(category=category_name_lower)
        cache.set(cache_key, articles, timeout=1800)
        cache.set(f'{cache_key}_next_page', next_page, timeout=1800)
    
    # Get seen articles from session or initialize empty set
    seen_articles = set(session.get(f'seen_{category_name_lower}_articles', []))
    
    # Filter out seen articles
    new_articles = [article for article in articles if article['id'] not in seen_articles]
    
    # Update seen articles in session
    seen_articles.update(article['id'] for article in new_articles)
    session[f'seen_{category_name_lower}_articles'] = list(seen_articles)
    
    # Store next page token in session for load more functionality
    session[f'category_{category_name_lower}_next_page'] = next_page
    
    return render_template('category.html',
                         articles=new_articles,
                         category=category_name_lower,
                         categories=VALID_CATEGORIES)

@main.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('main.index'))
    
    try:
        # Debug logging
        current_app.logger.info(f"Searching for query: {query}")
        current_app.logger.info(f"NewsService API Key: {news_service.api_key[:5]}...")
        
        # Use the news_service that's already configured for NewsData.io
        articles, next_page = news_service.search_news(query)
        
        # Debug logging
        current_app.logger.info(f"Found {len(articles)} articles")
        
        if not articles:
            flash('No results found for your search query.', 'info')
            return render_template('search.html', 
                                query=query,
                                articles=[],
                                total_results=0)
        
        # The articles are already formatted correctly by news_service.py
        # No need to reformat them as they match our template's expected structure
        return render_template('search.html', 
                            query=query,
                            articles=articles,
                            total_results=len(articles))
        
    except Exception as e:
        current_app.logger.error(f"Error in search: {str(e)}")
        flash('An error occurred while searching. Please try again.', 'error')
        return redirect(url_for('main.index'))

@main.route('/api/fact/random')
def random_fact():
    # Force a new fact by not using the cache
    fact = facts_service.get_daily_fact(force_new=True)
    return jsonify(fact)

@main.route('/api/news/global')
def more_global_news():
    """API endpoint to fetch more global news for the load more button"""
    # Get next page token from session
    next_page = session.get('global_next_page', '')
    shown_articles = session.get('shown_global_articles', [])
    
    # Fetch news with the next page token
    articles, new_next_page = news_service.get_headlines(page=next_page)
    
    # Filter out articles we've already shown
    filtered_articles = []
    for article in articles:
        if article['url'] not in shown_articles:
            filtered_articles.append(article)
            shown_articles.append(article['url'])
    
    # Update session with new next page token and shown articles
    session['global_next_page'] = new_next_page
    session['shown_global_articles'] = shown_articles
    
    return jsonify({
        'articles': filtered_articles,
        'has_more': bool(new_next_page) and len(filtered_articles) > 0
    })

@main.route('/api/news/indian')
def more_indian_news():
    """API endpoint to fetch more Indian news for the load more button"""
    # Get next page token from session
    next_page = session.get('indian_next_page', '')
    shown_articles = session.get('shown_indian_articles', [])
    
    # Fetch more Indian news with next page token
    articles, new_next_page = news_service.get_indian_news(page=next_page)
    
    # Filter out articles we've already shown
    filtered_articles = []
    for article in articles:
        if article['url'] not in shown_articles:
            filtered_articles.append(article)
            shown_articles.append(article['url'])
    
    # Update session with new next page token and shown articles
    session['indian_next_page'] = new_next_page
    session['shown_indian_articles'] = shown_articles
    
    return jsonify({
        'articles': filtered_articles,
        'has_more': bool(new_next_page) and len(filtered_articles) > 0
    })

@main.route('/api/news/category/<category_name>')
def more_category_news(category_name):
    """API endpoint to fetch more category news for the load more button"""
    # Get next page token from session
    next_page = session.get(f'category_{category_name}_next_page', '')
    shown_articles = session.get(f'shown_category_{category_name}_articles', [])
    
    # Fetch more category news with next page token
    articles, new_next_page = news_service.get_headlines(category=category_name, page=next_page)
    
    # Filter out articles we've already shown
    filtered_articles = []
    for article in articles:
        if article['url'] not in shown_articles:
            filtered_articles.append(article)
            shown_articles.append(article['url'])
    
    # Update session with new next page token and shown articles
    session[f'category_{category_name}_next_page'] = new_next_page
    session[f'shown_category_{category_name}_articles'] = shown_articles
    
    return jsonify({
        'articles': filtered_articles,
        'has_more': bool(new_next_page) and len(filtered_articles) > 0
    })

@main.route('/api/news/search')
def more_search_results():
    """API endpoint to fetch more search results for the load more button"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'articles': [], 'has_more': False})
    
    # Get next page token from session
    next_page = session.get(f'search_{query}_next_page', '')
    shown_articles = session.get(f'shown_search_{query}_articles', [])
    
    # Fetch more search results with next page token
    articles, new_next_page = news_service.search_news(query, page=next_page)
    
    # Filter out articles we've already shown
    filtered_articles = []
    for article in articles:
        if article['url'] not in shown_articles:
            filtered_articles.append(article)
            shown_articles.append(article['url'])
    
    # Update session with new next page token and shown articles
    session[f'search_{query}_next_page'] = new_next_page
    session[f'shown_search_{query}_articles'] = shown_articles
    
    return jsonify({
        'articles': filtered_articles,
        'has_more': bool(new_next_page) and len(filtered_articles) > 0
    })

@main.route('/settings')
def settings():
    """Route for user settings page"""
    return render_template('settings.html', categories=VALID_CATEGORIES)

@main.route('/location')
def location():
    return render_template('location.html')

@main.route('/local')
def local_news():
    """Route for local news based on user's location"""
    # Get location from session or default to None
    country = session.get('country')
    state = session.get('state')
    city = session.get('city')
    
    # Fetch local news with all location parameters
    articles = news_service.get_local_news(country=country, state=state, city=city)
    
    return render_template('local.html', 
                         articles=articles, 
                         country=country, 
                         state=state,
                         city=city) 