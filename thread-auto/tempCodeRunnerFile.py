from dotenv import load_dotenv
import os
from slack_bolt.app import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()

slack_app_token = os.getenv("SLACK_APP_TOKEN")
slack_bot_token = os.getenv("SLACK_BOT_TOKEN")

app = App(token=slack_bot_token)

# 출석 기록을 저장할 딕셔너리
attendance_record = {}

@app.message("쓰레드 인증")
def create_attendance(message, say, client):
    channel_id = message['channel']
    
    # 채널의 모든 멤버 가져오기
    response = client.conversations_members(channel=channel_id)
    user_ids = response['members']
    
    # 출석 기록 초기화
    global attendance_record
    attendance_record = {user_id: "❌" for user_id in user_ids}
    
    # 유저 이름 가져오기 및 표시
    names = []
    for user_id in user_ids:
        user_info = client.users_info(user=user_id)
        user_name = user_info['user']['real_name']
        names.append(f"{user_name} : {attendance_record[user_id]}")
    
    # 출석 체크 메시지 전송
    attendance_message = "\n".join(names)
    say(text=f"쓰레드 인증이 시작되었습니다!\n\n{attendance_message}")
    

@app.event("app_mention")
def handle_mention(event, say, client):
    user_id = event['user']
    channel_id = event['channel']
    ts = event['ts']
    
    # 출석 기록 업데이트
    if user_id in attendance_record:
        attendance_record[user_id] = "✅"
    
    # 업데이트된 출석 상태 표시
    updated_names = []
    for uid, status in attendance_record.items():
        user_info = client.users_info(user=uid)
        user_name = user_info['user']['real_name']
        updated_names.append(f"{user_name} : {status}")
    
    updated_message = "\n".join(updated_names)
    say(text=f"쓰레드 체크 업데이트:\n\n{updated_message}", thread_ts=ts)

# 봇 실행
handler = SocketModeHandler(app, slack_app_token)
handler.start()
