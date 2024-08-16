from dotenv import load_dotenv

import os
import requests # pip install requests

load_dotenv()

weather_api_key = os.getenv("WEATHER_API_KEY")
city_name = "london"

# API request URL
url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={weather_api_key}"

# Perform a GET request to obtain weather information
response = requests.get(url)
data = response.json()

# Print weather information
if response.status_code == 200:
    # Print current temperature, weather condition, humidity, and wind speed
    temperature = data['main']['temp'] - 273.0 # from Kelvin to Celsius
    weather = data['weather'][0]['description']
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']

    print(f"City: {city_name}")
    print(f"Temperature: {temperature:.1f}°C")
    print(f"Weather: {weather}")
    print(f"Humidity: {humidity}%")
    print(f"Wind Speed: {wind_speed} m/s")
else:
    print("Error:", response.status_code)