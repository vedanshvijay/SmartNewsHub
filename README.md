# SmartNewsHub

A Flask-based news aggregation platform that provides intelligent news recommendations.

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
FLASK_APP=run.py
FLASK_ENV=development
```

## Running the Application

1. Make sure your virtual environment is activated
2. Run the application:
```bash
python run.py
```

3. Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
SmartNewsHub/
├── app/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   ├── __init__.py
│   └── routes.py
├── venv/
├── .env
├── .gitignore
├── README.md
├── requirements.txt
└── run.py
```

## Features

- Modern Bootstrap-based UI
- Flask backend with blueprint structure
- Environment variable configuration
- Ready for development and production deployment 