import requests
from datetime import datetime, timedelta

class FactsService:
    def __init__(self):
        self.api_url = "https://uselessfacts.jsph.pl/api/v2/facts/random"
        self.cached_fact = None
        self.last_fetch_time = None

    def get_daily_fact(self, force_new=False):
        # If force_new is True, ignore cache and fetch new fact
        if not force_new and self.cached_fact and self.last_fetch_time:
            time_diff = datetime.now() - self.last_fetch_time
            if time_diff < timedelta(hours=24):
                return self.cached_fact

        try:
            response = requests.get(self.api_url)
            if response.status_code == 200:
                fact_data = response.json()
                self.cached_fact = {
                    'text': fact_data['text'],
                    'source': 'PlanetPulse',
                    'permalink': fact_data.get('permalink', '')
                }
                self.last_fetch_time = datetime.now()
                return self.cached_fact
            else:
                return {
                    'text': "Did you know? The internet is full of interesting facts, but sometimes they're hard to find!",
                    'source': 'PlanetPulse',
                    'permalink': ''
                }
        except Exception as e:
            print(f"Error fetching fact: {str(e)}")
            return {
                'text': "Did you know? Even the most reliable systems sometimes need a break!",
                'source': 'PlanetPulse',
                'permalink': ''
            } 