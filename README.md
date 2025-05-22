# PlanetPulse

PlanetPulse is an AI-powered news aggregator that provides personalized news content, real-time updates, and intelligent analysis of current events.

## Project Structure

- `flask_app/`
  - `__init__.py` - Core application setup
  - `auth.py` - User authentication and login management
  - `routes.py` - Application routes and endpoints
  - `models.py` - Database models
  - `news_service.py` - News fetching and processing
  - `ai_service.py` - AI analysis functionality
  - `personalization_service.py` - User personalization and recommendations
  - `sitemap.py` - SEO functionality
  - `facts_service.py` - Daily facts feature
  - `utils/` - Essential utilities
  - `templates/` - HTML templates
  - `static/` - Static assets (CSS, JS, images)

## Features

- Real-time news updates
- AI-powered article summaries
- Personalized news feed
- Category-based browsing
- Local news integration
- Breaking news alerts

## Setup

1. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables in a `.env` file:
   ```
   SECRET_KEY=your_secret_key
   FLASK_APP=app.py
   FLASK_ENV=development
   NEWSDATA_API_KEY=your_api_key
   NEWSDATA_API_KEY_FALLBACK=your_fallback_api_key
   DATABASE_URL=your_database_url
   ```

3. Run the application:
   ```bash
   python app.py
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🎯 Vision

PlanetPulse aims to revolutionize how people consume news by providing a personalized, intelligent, and user-friendly platform that delivers relevant content while maintaining journalistic integrity and user privacy.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to all the open-source projects that made this possible
- Special thanks to the Flask and Bootstrap communities
- Inspired by modern news aggregation platforms 