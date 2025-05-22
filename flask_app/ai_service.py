"""
AI Service Module for SmartNewsHub

This module provides AI-powered analysis of news articles using various NLP (Natural Language Processing) techniques.
It utilizes the Hugging Face Transformers library for advanced text processing tasks.
"""

import logging
from transformers import pipeline  # Hugging Face's pipeline for easy model loading
import numpy as np  # Numerical computing library
from textblob import TextBlob  # Simple NLP library for text processing
from collections import Counter  # For counting occurrences of elements
import re  # Regular expressions for text pattern matching

# Configure logging to track errors and operations
logger = logging.getLogger(__name__)

class AIService:
    """
    A service class that provides AI-powered analysis of news articles.
    
    This class initializes and manages various AI models for:
    - Text summarization
    - Sentiment analysis
    - Topic classification
    """
    
    def __init__(self):
        """
        Initialize AI models using Hugging Face's pipeline.
        
        The pipeline() function automatically downloads and loads pre-trained models:
        - summarizer: For generating article summaries
        - sentiment_analyzer: For analyzing text sentiment
        - zero_shot_classifier: For topic classification without training
        """
        try:
            # Initialize transformers pipeline for each task
            self.summarizer = pipeline("summarization")
            self.sentiment_analyzer = pipeline("sentiment-analysis")
            self.zero_shot_classifier = pipeline("zero-shot-classification")
        except Exception as e:
            logger.error(f"Error initializing AI models: {str(e)}")
            # Fallback initialization if models fail to load
            self.summarizer = None
            self.sentiment_analyzer = None
            self.zero_shot_classifier = None

    def analyze_article(self, article_text, article_title):
        """
        Main method to analyze an article using various AI techniques.
        
        Args:
            article_text (str): The main content of the article
            article_title (str): The title of the article
            
        Returns:
            dict: A dictionary containing:
                - summary: Generated article summary
                - topics: Identified topics
                - sentiment: Sentiment analysis results
                - tags: Generated tags
        """
        try:
            # Generate summary using the summarization model
            summary = self._generate_summary(article_text)
            
            # Extract main topics from the article
            topics = self._extract_topics(article_text, article_title)
            
            # Analyze the sentiment of the article
            sentiment = self._analyze_sentiment(article_text)
            
            # Generate relevant tags based on content
            tags = self._generate_tags(article_text, topics)
            
            return {
                'summary': summary,
                'topics': topics,
                'sentiment': sentiment,
                'tags': tags
            }
        except Exception as e:
            logger.error(f"Error analyzing article: {str(e)}")
            return None

    def _generate_summary(self, text, max_length=150):
        """
        Generate a concise summary of the article text.
        
        Args:
            text (str): The article text to summarize
            max_length (int): Maximum length of the summary
            
        Returns:
            str: Generated summary of the article
        """
        try:
            # Fallback to simple text truncation if summarizer is not available
            if not self.summarizer:
                return text[:max_length] + "..."
            
            # Calculate appropriate summary length based on input length
            input_length = len(text.split())
            if input_length < 100:
                # For very short texts, use a shorter summary
                summary_length = min(max_length, max(30, input_length // 2))
            else:
                # For longer texts, use a proportion of the input length
                summary_length = min(max_length, max(50, input_length // 3))
            
            # Split text into chunks if too long for the model
            chunks = self._split_text(text)
            summaries = []
            
            # Process each chunk and combine summaries
            for chunk in chunks:
                summary = self.summarizer(
                    chunk,
                    max_length=summary_length,
                    min_length=max(30, summary_length // 2),
                    do_sample=False
                )
                summaries.append(summary[0]['summary_text'])
            
            return " ".join(summaries)
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return text[:max_length] + "..."

    def _extract_topics(self, text, title):
        """
        Extract main topics from the article using zero-shot classification.
        
        Args:
            text (str): The article text
            title (str): The article title
            
        Returns:
            list: List of identified topics
        """
        try:
            # Combine title and text for better topic extraction
            combined_text = f"{title} {text}"
            
            # Define possible topics for classification
            candidate_topics = [
                "politics", "business", "technology", "sports", "entertainment",
                "health", "science", "education", "environment", "world"
            ]
            
            # Use zero-shot classification if available
            if self.zero_shot_classifier:
                result = self.zero_shot_classifier(
                    combined_text,
                    candidate_topics,
                    multi_label=True
                )
                # Return topics with confidence score > 0.5
                return [topic for topic, score in zip(result['labels'], result['scores']) if score > 0.5]
            
            # Fallback to basic keyword extraction
            return self._extract_keywords(combined_text)
        except Exception as e:
            logger.error(f"Error extracting topics: {str(e)}")
            return []

    def _analyze_sentiment(self, text):
        """
        Analyze the sentiment of the article text.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            dict: Dictionary containing sentiment label and confidence score
        """
        try:
            # Use transformer-based sentiment analyzer if available
            if self.sentiment_analyzer:
                result = self.sentiment_analyzer(text[:512])[0]
                return {
                    'label': result['label'],
                    'score': result['score']
                }
            
            # Fallback to TextBlob for basic sentiment analysis
            analysis = TextBlob(text)
            return {
                'label': 'POSITIVE' if analysis.sentiment.polarity > 0 else 'NEGATIVE',
                'score': abs(analysis.sentiment.polarity)
            }
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {'label': 'NEUTRAL', 'score': 0.0}

    def _generate_tags(self, text, topics):
        """
        Generate relevant tags for the article.
        
        Args:
            text (str): The article text
            topics (list): Previously identified topics
            
        Returns:
            list: List of generated tags
        """
        try:
            # Combine topics with extracted keywords
            keywords = self._extract_keywords(text)
            tags = list(set(topics + keywords))  # Remove duplicates using set
            
            # Limit to top 5 most relevant tags
            return tags[:5]
        except Exception as e:
            logger.error(f"Error generating tags: {str(e)}")
            return []

    def _extract_keywords(self, text):
        """
        Extract keywords from text using basic NLP techniques.
        
        Args:
            text (str): The text to extract keywords from
            
        Returns:
            list: List of extracted keywords
        """
        try:
            # Remove special characters and convert to lowercase
            text = re.sub(r'[^\w\s]', '', text.lower())
            
            # Define common English stop words to filter out
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            words = [word for word in text.split() if word not in stop_words]
            
            # Count word frequencies using Counter
            word_freq = Counter(words)
            
            # Return top 5 most common words as keywords
            return [word for word, _ in word_freq.most_common(5)]
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            return []

    def _split_text(self, text, max_length=1024):
        """
        Split long text into smaller chunks for processing.
        
        Args:
            text (str): The text to split
            max_length (int): Maximum length of each chunk
            
        Returns:
            list: List of text chunks
        """
        try:
            words = text.split()
            chunks = []
            current_chunk = []
            current_length = 0
            
            # Split text into chunks of maximum length
            for word in words:
                if current_length + len(word) + 1 <= max_length:
                    current_chunk.append(word)
                    current_length += len(word) + 1
                else:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = [word]
                    current_length = len(word)
            
            # Add the last chunk if it exists
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            
            return chunks
        except Exception as e:
            logger.error(f"Error splitting text: {str(e)}")
            return [text] 