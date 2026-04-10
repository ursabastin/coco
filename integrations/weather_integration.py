import requests

class WeatherIntegration:
    def __init__(self):
        # Using free wttr.in service (no API key needed)
        self.base_url = "https://wttr.in"
    
    def get_weather(self, city=""):
        """Get weather for a city"""
        try:
            # Format 3 gives concise output
            url = f"{self.base_url}/{city}?format=3"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return response.text.strip()
            else:
                return "Could not fetch weather"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_detailed_weather(self, city=""):
        """Get detailed weather forecast"""
        try:
            url = f"{self.base_url}/{city}?format=j1"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                current = data['current_condition'][0]
                
                temp = current['temp_C']
                feels_like = current['FeelsLikeC']
                desc = current['weatherDesc'][0]['value']
                humidity = current['humidity']
                
                return f"Current: {temp}°C (feels like {feels_like}°C), {desc}, Humidity {humidity}%"
            else:
                return "Could not fetch weather"
        except Exception as e:
            return f"Error: {str(e)}"

# Test script
if __name__ == "__main__":
    weather = WeatherIntegration()
    print(weather.get_weather("London"))
    print(weather.get_detailed_weather("London"))
