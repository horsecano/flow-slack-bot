from dotenv import load_dotenv

import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()

slack_app_token = os.getenv("SLACK_APP_TOKEN")
slack_bot_token = os.getenv("SLACK_BOT_TOKEN")

app = App(token=slack_bot_token)

@app.event("message")
def get_user_name(args, client):
    data = args.__dict__

    user_id = data.get('message').get('user')

    user_info = client.users_info(user=user_id) # Need users:read permission scope!
    user_name = user_info['user']['real_name']

    print(f"User Name: {user_name}")


handler = SocketModeHandler(app, slack_app_token)
handler.start()
