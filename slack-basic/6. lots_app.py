from dotenv import load_dotenv

import os
from slack_bolt.app import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import random

load_dotenv()

slack_app_token = os.getenv("SLACK_APP_TOKEN")
slack_bot_token = os.getenv("SLACK_BOT_TOKEN")

app = App(token=slack_bot_token)

@app.event({"type": "message", "subtype": None})
def message(args, say, client):
    data = args.__dict__

    user_input = data.get('event').get('text')
    event_ts = data.get('event').get('ts')
    channel_id = data.get('event').get("channel")

    if user_input == "LOTS":

        # get list of user's id in channel(Need channels:read permission scope!)
        members = client.conversations_members(channel=channel_id)["members"]

        while True:
            picked_user_id = random.choice(members)

            picked_user_info = client.users_info(user=picked_user_id)
            picked_user_name = picked_user_info['user']['real_name']

            if picked_user_name != "my_app": # exclude app is picked(Need to change to your app's name)
                break

        say(channel=channel_id, text=f"Picked User: {picked_user_name}",
            thread_ts=event_ts, icon_emoji="slot_machine", username="Lots App")


# NotImpement cases of edit and delete in this example.
@app.event({"type": "message", "subtype": "message_changed"})
def message_edit(args, say, client):
    return

@app.event({"type": "message", "subtype": "message_deleted"})
def message_delete(args, client):
    return

handler = SocketModeHandler(app, slack_app_token)
handler.start()