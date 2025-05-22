from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    preferences = db.relationship('UserPreferences', backref='user', uselist=False)
    engagement = db.relationship('UserEngagement', backref='user', uselist=False)
    achievements = db.relationship('UserAchievements', backref='user')
    reading_history = db.relationship('ReadingHistory', backref='user')

class UserPreferences(db.Model):
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    categories = db.Column(db.Text, default='[]')  # JSON array of preferred categories
    sources = db.Column(db.Text, default='[]')  # JSON array of preferred news sources
    reading_time = db.Column(db.Float, default=0.0)  # Average reading time in seconds
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class Article(db.Model):
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.String(255), unique=True, nullable=False)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    url = db.Column(db.String(500))
    image_url = db.Column(db.String(500))
    source = db.Column(db.String(100))
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tags = db.relationship('ArticleTags', backref='article', uselist=False)
    categories = db.relationship('ArticleCategory', backref='article')
    reading_history = db.relationship('ReadingHistory', backref='article')

class ReadingHistory(db.Model):
    __tablename__ = 'reading_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read_time = db.Column(db.Float)  # Time spent reading in seconds
    completed = db.Column(db.Boolean, default=False)
    interaction_type = db.Column(db.String(50))  # read, share, comment, etc.

class UserEngagement(db.Model):
    __tablename__ = 'user_engagement'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    points = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    streak_days = db.Column(db.Integer, default=0)
    badges = db.Column(db.Text, default='[]')  # JSON array of earned badges
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)

class ArticleTags(db.Model):
    __tablename__ = 'article_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), unique=True, nullable=False)
    tags = db.Column(db.Text, default='[]')  # JSON array of AI-generated tags
    summary = db.Column(db.Text)  # AI-generated summary
    sentiment = db.Column(db.String(50))  # AI-analyzed sentiment
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    articles = db.relationship('ArticleCategory', backref='category')

class ArticleCategory(db.Model):
    __tablename__ = 'article_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('article_id', 'category_id', name='unique_article_category'),
    )

class UserAchievements(db.Model):
    __tablename__ = 'user_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_type = db.Column(db.String(50), nullable=False)  # reader, explorer, critic, etc.
    progress = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    unlocked_at = db.Column(db.DateTime)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'achievement_type', name='unique_user_achievement'),
    ) 