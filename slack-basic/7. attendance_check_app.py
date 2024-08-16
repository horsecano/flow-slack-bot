from dotenv import load_dotenv

import os
from slack_bolt.app import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import time

load_dotenv()

slack_app_token = os.getenv("SLACK_APP_TOKEN")
slack_bot_token = os.getenv("SLACK_BOT_TOKEN")

app = App(token=slack_bot_token)

record = {}

@app.event({"type": "message", "subtype": None})
def message(args, say, client):
    data = args.__dict__

    user_input = data.get('event').get('text')
    event_ts = data.get('event').get('ts')
    channel_id = data.get('event').get("channel")
    user_id = data.get('message').get('user')

    now = time.localtime()

    current_month = now.tm_mon
    current_day = now.tm_mday

    current_hour = now.tm_hour
    current_minute = now.tm_min

    if user_input == "check":

        user_info = client.users_info(user=user_id)
        user_name = user_info['user']['real_name']

        try:
            record[f"{current_month}/{current_day}"][user_name] = f"{current_hour}:{current_minute}"
        except: # First Attendance of Today
            record[f"{current_month}/{current_day}"] = {user_name : f"{current_hour}:{current_minute}"}

        say(channel=channel_id, text=f"Attendance Time of {current_month}/{current_day} -> {current_hour}:{current_minute}",
            thread_ts=event_ts, icon_emoji="calendar", username="Time Check App")

    elif user_input == "today result":

        result = ""

        today_record = record.get(f"{current_month}/{current_day}", {})

        for user_name in today_record.keys():
            result += f"{user_name} -> {today_record.get(user_name)}\n"

        say(channel=channel_id, text=result, thread_ts=event_ts,
            icon_emoji="calendar", username="Time Check App")


# NotImpement cases of edit and delete in this example.
@app.event({"type": "message", "subtype": "message_changed"})
def message_edit(args, say, client):
    return

@app.event({"type": "message", "subtype": "message_deleted"})
def message_delete(args, client):
    return

handler = SocketModeHandler(app, slack_app_token)
handler.start()