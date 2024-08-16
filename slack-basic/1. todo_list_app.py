from dotenv import load_dotenv

import os
import json
from slack_bolt.app import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()

slack_app_token = os.getenv("SLACK_APP_TOKEN")
slack_bot_token = os.getenv("SLACK_BOT_TOKEN")

app = App(token=slack_bot_token)

json_path = './record.json'

def load_record():
    with open(json_path, 'r') as f:
        data = json.load(f)

    return data

def add_record(item):
    with open(json_path, 'r') as f:
        data = json.load(f)

    if item not in data:
        data.append(item)
        with open(json_path, 'w') as f:
            json.dump(data, f)
        return True
    return False

def delete_record(item):
    with open(json_path, 'r') as f:
        data = json.load(f)

    if item in data:
        data.remove(item)

        with open(json_path, 'w') as f:
            json.dump(data, f)
        return True
    return False

def clear_record():
    with open(json_path, 'w') as f:
        json.dump([], f)


@app.event({"type": "message", "subtype": None})
def message(args, say):
    data = args.__dict__

    user_input = data.get('event').get('text')
    event_ts = data.get('event').get('ts')
    channel_id = data.get('event').get("channel")

    # Add New Item
    if len(user_input) > 4 and user_input[0:4] == "add:": # check length of user input to prevent error!
        item = user_input[4:].strip() # strip(): remove space
        result = add_record(item)

        if result:
            say(channel=channel_id, text=f"Add New Item: {item}", thread_ts=event_ts,
                icon_emoji="green_book", username="TODO List App")
        else:
            say(channel=channel_id, text=f"{item} is already existed", thread_ts=event_ts,
                icon_emoji="green_book", username="TODO List App")


    # Delete Item
    elif len(user_input) > 7 and user_input[0:7] == "delete:": # check length of user input to prevent error!
        item = user_input[7:].strip()  # strip(): remove space
        result = delete_record(item)

        if result:
            say(channel=channel_id, text=f"Delete New Item: {item}", thread_ts=event_ts,
                icon_emoji="green_book", username="TODO List App")
        else:
            say(channel=channel_id, text=f"{item} is not existed", thread_ts=event_ts,
                icon_emoji="green_book", username="TODO List App")

    # Lookup Item List
    elif user_input == "lookup":
        item_list = load_record()
        say(channel=channel_id, text=f"Item List: {item_list}", thread_ts=event_ts,
            icon_emoji="green_book", username="TODO List App")

    # Clear Item List
    elif user_input == "clear":
        clear_record()
        say(channel=channel_id, text=f"Clear TODO List!", thread_ts=event_ts,
            icon_emoji="green_book", username="TODO List App")

    else:
        return


# NotImpement cases of edit and delete in this example.
@app.event({"type": "message", "subtype": "message_changed"})
def message_edit(args, say, client):
    return

@app.event({"type": "message", "subtype": "message_deleted"})
def message_delete(args, client):
    return

handler = SocketModeHandler(app, slack_app_token)
handler.start()