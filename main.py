from dotenv import load_dotenv
import os
from slack_bolt.app import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from datetime import datetime
import schedule
import time

# Load environment variables
load_dotenv()

slack_app_token = os.getenv("SLACK_APP_TOKEN")
slack_bot_token = os.getenv("SLACK_BOT_TOKEN")


app = App(token=slack_bot_token)

attendance_record_channel_1 = {}
attendance_record_channel_2 = {}
initial_message_ts_channel_1 = None
initial_message_ts_channel_2 = None
channel_id_1 = "C07HVEQ8S0G" 
channel_id_2 = "C079BDBTXDY" 

def start_thread_check(channel_id, attendance_record, initial_message_ts):
    response = app.client.conversations_members(channel=channel_id)
    user_ids = response['members']

    bot_id = app.client.auth_test()["user_id"]

    attendance_record.clear()
    attendance_record.update({user_id: "❌" for user_id in user_ids if user_id != bot_id})

    today_date = datetime.now().strftime("%Y-%m-%d")

    names = []
    for user_id in attendance_record.keys():
        user_info = app.client.users_info(user=user_id)
        user_name = user_info['user']['real_name']
        names.append(f"{user_name} : {attendance_record[user_id]}")

    attendance_message = "\n".join(names)
    result = app.client.chat_postMessage(channel=channel_id, text=f"{today_date} - 쓰레드 인증이 시작되었습니다! (매일 11:59PM까지 인증 )\n\n{attendance_message}")
    
    initial_message_ts = result['ts']
    return initial_message_ts

def end_thread_check(channel_id, attendance_record):
    today_date = datetime.now().strftime("%Y-%m-%d")

    unverified_users = [uid for uid, status in attendance_record.items() if status == "❌"]
    unverified_names = []
    for user_id in unverified_users:
        user_info = app.client.users_info(user=user_id)
        user_name = user_info['user']['real_name']
        unverified_names.append(user_name)
    
    if unverified_names:
        unverified_message = f"{today_date} 쓰레드 미인증자 - {', '.join(unverified_names)}"
    else:
        unverified_message = f"{today_date} - 모든 사용자가 인증을 완료했습니다!"

    app.client.chat_postMessage(channel=channel_id, text=unverified_message)

    attendance_record.clear()

def check_results(channel_id, attendance_record):
    today_date = datetime.now().strftime("%Y-%m-%d")

    verified_users = [uid for uid, status in attendance_record.items() if status == "✅"]
    unverified_users = [uid for uid, status in attendance_record.items() if status == "❌"]

    verified_names = []
    unverified_names = []

    for user_id in verified_users:
        user_info = app.client.users_info(user=user_id)
        user_name = user_info['user']['real_name']
        verified_names.append(user_name)

    for user_id in unverified_users:
        user_info = app.client.users_info(user=user_id)
        user_name = user_info['user']['real_name']
        unverified_names.append(user_name)

    results_message = (
        f"{today_date} 쓰레드 인증 결과\n"
        f"인증자✅ : {', '.join(verified_names) if verified_names else '없음'}\n"
        f"미인증🫠 : {', '.join(unverified_names) if unverified_names else '없음'}"
    )

    app.client.chat_postMessage(channel=channel_id, text=results_message)

# Schedule thread check start and end times for both channels
schedule.every().day.at("00:01").do(lambda: globals().update(initial_message_ts_channel_1=start_thread_check(channel_id_1, attendance_record_channel_1, initial_message_ts_channel_1)))
schedule.every().day.at("00:01").do(lambda: globals().update(initial_message_ts_channel_2=start_thread_check(channel_id_2, attendance_record_channel_2, initial_message_ts_channel_2)))
schedule.every().day.at("23:59").do(lambda: end_thread_check(channel_id_1, attendance_record_channel_1))
schedule.every().day.at("23:59").do(lambda: end_thread_check(channel_id_2, attendance_record_channel_2))

@app.message("쓰레드 인증")
def manual_start_thread_check(message, say):
    say("입력 완료...")
    channel_id = message['channel']
    if channel_id == channel_id_1:
        globals().update(initial_message_ts_channel_1=start_thread_check(channel_id_1, attendance_record_channel_1, initial_message_ts_channel_1))
    elif channel_id == channel_id_2:
        globals().update(initial_message_ts_channel_2=start_thread_check(channel_id_2, attendance_record_channel_2, initial_message_ts_channel_2))

@app.message("결과")
def show_results(message, say):
    say("입력 완료...")
    channel_id = message['channel']
    if channel_id == channel_id_1:
        check_results(channel_id_1, attendance_record_channel_1)
    elif channel_id == channel_id_2:
        check_results(channel_id_2, attendance_record_channel_2)

@app.event("app_mention")
def handle_mention(event, say, client):
    global initial_message_ts_channel_1, initial_message_ts_channel_2

    user_id = event['user']
    channel_id = event['channel']
    mentioned_ts = event.get('ts')  # Get the timestamp of the message that mentioned the bot

    # Automatically respond with "인증 확인!" in the thread and react with a ✅ emoji
    client.reactions_add(channel=channel_id, name="white_check_mark", timestamp=mentioned_ts)

    if channel_id == channel_id_1:
        if initial_message_ts_channel_1 is None:
            say("초기 메시지 타임스탬프가 설정되지 않았습니다. 먼저 쓰레드 인증을 시작하세요.")
            return

        if user_id in attendance_record_channel_1:
            attendance_record_channel_1[user_id] = "✅"
        else:
            say(f"출석 기록에서 유저를 찾을 수 없습니다: <@{user_id}>")

        updated_names = []
        for uid, status in attendance_record_channel_1.items():
            user_info = client.users_info(user=uid)
            user_name = user_info['user']['real_name']
            updated_names.append(f"{user_name} : {status}")

        updated_message = "\n".join(updated_names)
        today_date = datetime.now().strftime("%Y-%m-%d")

        client.chat_update(
            channel=channel_id_1,
            ts=initial_message_ts_channel_1,
            text=f"{today_date} - 쓰레드 인증이 시작되었습니다!\n\n{updated_message}"
        )

    elif channel_id == channel_id_2:
        if initial_message_ts_channel_2 is None:
            say("초기 메시지 타임스탬프가 설정되지 않았습니다. 먼저 쓰레드 인증을 시작하세요.")
            return

        if user_id in attendance_record_channel_2:
            attendance_record_channel_2[user_id] = "✅"
        else:
            say(f"쓰레드 인증 기록에서 유저를 찾을 수 없습니다: <@{user_id}>")

        updated_names = []
        for uid, status in attendance_record_channel_2.items():
            user_info = client.users_info(user=uid)
            user_name = user_info['user']['real_name']
            updated_names.append(f"{user_name} : {status}")

        updated_message = "\n".join(updated_names)
        today_date = datetime.now().strftime("%Y-%m-%d")

        client.chat_update(
            channel=channel_id_2,
            ts=initial_message_ts_channel_2,
            text=f"{today_date} - 쓰레드 인증이 시작되었습니다!\n\n{updated_message}"
        )

# Start the bot and scheduler
handler = SocketModeHandler(app, slack_app_token)
handler.start()

while True:
    schedule.run_pending()
    time.sleep(1)
