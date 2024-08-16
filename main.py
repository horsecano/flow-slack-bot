from dotenv import load_dotenv
import os
from slack_bolt.app import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from datetime import datetime
import schedule
import time

load_dotenv()

slack_app_token = os.getenv("SLACK_APP_TOKEN")
slack_bot_token = os.getenv("SLACK_BOT_TOKEN")

app = App(token=slack_bot_token)

# 출석 기록을 저장할 딕셔너리
attendance_record = {}
initial_message_ts = None
channel_id = "C079BDBTXDY"  # 여기에 실제 채널 ID를 입력하세요

def start_thread_check():
    global initial_message_ts
    global attendance_record
    
    # 채널의 모든 멤버 가져오기
    response = app.client.conversations_members(channel=channel_id)
    user_ids = response['members']

    # 봇 자신의 ID 가져오기
    bot_id = app.client.auth_test()["user_id"]

    # 봇 자신을 제외한 출석 기록 초기화
    attendance_record = {user_id: "❌" for user_id in user_ids if user_id != bot_id}

    # 오늘 날짜 가져오기
    today_date = datetime.now().strftime("%Y-%m-%d")

    # 유저 이름 가져오기 및 표시
    names = []
    for user_id in attendance_record.keys():
        user_info = app.client.users_info(user=user_id)
        user_name = user_info['user']['real_name']
        names.append(f"{user_name} : {attendance_record[user_id]}")

    # 출석 체크 메시지 전송 및 메시지 ts 저장
    attendance_message = "\n".join(names)
    result = app.client.chat_postMessage(channel=channel_id, text=f"{today_date} - 쓰레드 인증이 시작되었습니다! (매일 11:59PM까지 인증 )\n\n{attendance_message}")

    # 전송된 메시지의 ts를 저장하여 나중에 업데이트에 사용
    initial_message_ts = result['ts']


def end_thread_check():
    global initial_message_ts
    global attendance_record
    
    # 오늘 날짜 가져오기
    today_date = datetime.now().strftime("%Y-%m-%d")

    # 인증을 못한 사람 목록 가져오기
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

    # 미인증자 목록 전송
    app.client.chat_postMessage(channel=channel_id, text=unverified_message)

    # 출석 기록 초기화
    attendance_record = {}
    initial_message_ts = None


# 매일 00:01에 쓰레드 인증 시작
schedule.every().day.at("00:01").do(start_thread_check)

# 매일 23:59에 쓰레드 인증 종료 및 결과 전송
schedule.every().day.at("23:59").do(end_thread_check)

@app.message("쓰레드 인증")
def manual_start_thread_check(message, say, client):
    start_thread_check()
    say("수동으로 쓰레드 인증이 시작되었습니다!")

@app.event("app_mention")
def handle_mention(event, say, client):
    global initial_message_ts

    user_id = event['user']
    channel_id = event['channel']

    # 출석 기록 업데이트
    if user_id in attendance_record:
        attendance_record[user_id] = "✅"
    else:
        say(f"출석 기록에서 유저를 찾을 수 없습니다: <@{user_id}>")

    # 업데이트된 출석 상태 표시
    updated_names = []
    for uid, status in attendance_record.items():
        user_info = client.users_info(user=uid)
        user_name = user_info['user']['real_name']
        updated_names.append(f"{user_name} : {status}")

    updated_message = "\n".join(updated_names)
    
    # 오늘 날짜 가져오기
    today_date = datetime.now().strftime("%Y-%m-%d")

    # 기존 메시지를 업데이트
    client.chat_update(
        channel=channel_id,
        ts=initial_message_ts,
        text=f"{today_date} - 쓰레드 인증이 시작되었습니다!\n\n{updated_message}"
    )


# 봇 실행
handler = SocketModeHandler(app, slack_app_token)
handler.start()

# 스케줄러 실행
while True:
    schedule.run_pending()
    time.sleep(1)
