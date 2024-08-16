from dotenv import load_dotenv

import os
from slack_bolt.app import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import requests

load_dotenv()

slack_app_token = os.getenv("SLACK_APP_TOKEN")
slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
weather_api_key = os.getenv("WEATHER_API_KEY")

app = App(token=slack_bot_token)

def use_weather_api(city_name):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={weather_api_key}"

    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        temperature = data['main']['temp'] - 273.0
        weather = data['weather'][0]['description']

        return {"temperature": temperature, "weather": weather}

    else: # Invalid city name or api key
        return None

def get_weather_icon(weather):
    if "clear" in weather:
        return "sunny"
    elif "cloud" in weather:
        return "cloud"
    elif "rain" in weather:
        return "rain_cloud"
    elif "snow" in weather:
        return "snowflake"
    else:
        return "zap"


@app.event({"type": "message", "subtype": None})
def message(args, say):
    data = args.__dict__

    user_input = data.get('event').get('text')
    event_ts = data.get('event').get('ts')
    channel_id = data.get('event').get("channel")

    if "weather" in user_input:

        # split example: "hi! hello world" -> ["hi!", "hello", "world"]
        city_name = user_input.split()[-1].rstrip("?") # last word of input sentence and remove question mark
        result = use_weather_api(city_name)

        if result is not None:

            temperature = result.get("temperature")
            weather = result.get("weather")

            icon_emoji = get_weather_icon(weather)

            say(channel=channel_id, text=f"City: {city_name}, temperature: {temperature:.1f}°C, weather: {weather}",
                thread_ts=event_ts, icon_emoji=icon_emoji, username="Weather App")


# NotImpement cases of edit and delete in this example.
@app.event({"type": "message", "subtype": "message_changed"})
def message_edit(args, say, client):
    return

@app.event({"type": "message", "subtype": "message_deleted"})
def message_delete(args, client):
    return

handler = SocketModeHandler(app, slack_app_token)
handler.start()