from dotenv import load_dotenv

import os
import json
from slack_bolt.app import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import googletrans

load_dotenv()

slack_app_token = os.getenv("SLACK_APP_TOKEN")
slack_bot_token = os.getenv("SLACK_BOT_TOKEN")

app = App(token=slack_bot_token)

json_path = './history.json'

translator = googletrans.Translator()

def is_deleted_message(data):
    if data.get("message", {}).get("message", {}).get("subtype", "") == "tombstone":
        return True
    else:
        return False

def load_timestamp(event_ts):
    with open(json_path, 'r') as f:
        data = json.load(f)
        return data.get(event_ts)

def add_timestamp(event_ts, thread_ts):
    with open(json_path, 'r') as f:
        data = json.load(f)

    data[event_ts] = thread_ts

    with open(json_path, 'w') as f:
        json.dump(data, f)

def delete_timestamp(event_ts):
    with open(json_path, 'r') as f:
        data = json.load(f)

    del data[event_ts]

    with open(json_path, 'w') as f:
        json.dump(data, f)

@app.event({"type": "message", "subtype": None})
def message(args, say):
    data = args.__dict__

    user_input = data.get('event').get('text')
    event_ts = data.get('event').get('ts')
    channel_id = data.get('event').get("channel")

    translated_result = translator.translate(user_input, dest='fr')
    translated_text = translated_result.text

    thread_ts = say(channel=channel_id, text=translated_text, thread_ts=event_ts,
                    icon_emoji="earth_americas", username="Translator")
    thread_ts = thread_ts.get("ts")
    add_timestamp(event_ts, thread_ts)

@app.event({"type": "message", "subtype": "message_changed"})
def message_edit(args, say, client):
    data = args.__dict__

    user_input = data.get('event').get('message').get('text')
    previous_message = data.get('event').get('previous_message').get('text')
    event_ts = data.get('event').get('previous_message').get('ts')
    channel_id = data.get('event').get("channel")
    sub_type = data.get('event').get('message').get('subtype')

    if sub_type == 'bot_message': # To prevent the bot from responding to its own message
        return

    if is_deleted_message(data):
        thread_ts = load_timestamp(event_ts)
        try:
            client.chat_delete(channel=channel_id, ts=thread_ts)
            delete_timestamp(event_ts)
        except:
            pass
        return

    if previous_message != user_input:  # "To prevent other messages within the thread from being modified together.

        translated_result = translator.translate(user_input, dest='fr')
        translated_text = translated_result.text

        thread_ts = load_timestamp(event_ts)

        if thread_ts is not None:  # if bot message is already existed
            client.chat_update(channel=channel_id, text=translated_text, ts=thread_ts,
                               icon_emoji="earth_americas", username="Translator")

        else:  # if bot message is not existed
            thread_ts = say(channel=channel_id, text=translated_text, thread_ts=event_ts,
                            icon_emoji="earth_americas", username="Translator")
            thread_ts = thread_ts.get("ts")
            add_timestamp(event_ts, thread_ts)

@app.event({"type": "message", "subtype": "message_deleted"})
def message_delete(args, client):
    data = args.__dict__

    event_ts = data.get('event').get('previous_message').get('ts')
    channel_id = data.get('event').get("channel")

    thread_ts = load_timestamp(event_ts)

    if thread_ts is not None:
        try:
            client.chat_delete(channel=channel_id, ts=thread_ts)
            delete_timestamp(event_ts)
        except:
            pass


handler = SocketModeHandler(app, slack_app_token)
handler.start()