# PlanetPulse

A modern news aggregation platform that brings you the latest news from around the world.

## Features

- Real-time news updates
- Multiple news categories
- Customizable news feed
- Responsive design
- User-friendly interface

## Installation

1. Clone the repository
2. Install dependencies
3. Run the application

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following content:
```
SECRET_KEY=your-secret-key-here
NEWSDATA_API_KEY=your-newsdata-io-api-key-here
```

## API Integration

This application uses the NewsData.io API for fetching news content. You will need to:

1. Register at [NewsData.io](https://newsdata.io/) to get an API key
2. Add your API key to the `.env` file as shown above
3. The free tier of NewsData.io has some limitations:
   - Limited number of requests per day
   - Some filtering parameters might not work (country, etc.)
   - The API uses a pagination system with "nextPage" tokens instead of page numbers

## Running the Application

1. Make sure your virtual environment is activated
2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to `http://localhost:5001`

## Project Structure

```
SmartNewsHub/
├── flask_app/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   ├── __init__.py
│   ├── routes.py
│   ├── news_service.py
│   └── facts_service.py
├── venv/
├── .env
├── .gitignore
├── README.md
├── requirements.txt
├── app.py
├── Procfile
├── render.yaml
└── railway.toml
```

## Features

- Modern Bootstrap-based UI with responsive design
- Flask backend with blueprint structure
- "Load More" functionality for all news sections
- Daily facts feature with refresh capability
- Environment variable configuration
- Ready for deployment to Heroku, Render, or Railway
- Caching system to reduce API calls
- Background task scheduler for updating news content

## Deployment Notes

The application is configured for deployment to multiple platforms:

- **Heroku**: Use the included Procfile
- **Render**: Use the render.yaml configuration
- **Railway**: Use the railway.toml configuration

Make sure to set the following environment variables in your deployment platform:
- `NEWSDATA_API_KEY`: Your NewsData.io API key
- `SECRET_KEY`: A secret key for Flask sessions

## Troubleshooting API Issues

If you encounter issues with the NewsData.io API:

1. Check that your API key is correctly set in the environment variables
2. The free tier has limited requests per day - you might hit rate limits
3. Some filtering parameters (country, category) might return 422 errors in the free tier
4. The app has been modified to work with these limitations by:
   - Using the nextPage token for pagination
   - Relying on basic parameters that work with the free tier
   - Implementing proper error handling 