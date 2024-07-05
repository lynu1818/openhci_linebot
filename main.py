from flask import Flask, request

import json

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageSendMessage, FlexSendMessage, FollowEvent, PostbackEvent, TextSendMessage, LocationSendMessage, QuickReply, QuickReplyButton, MessageAction, DatetimePickerAction

import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from geopy.geocoders import Nominatim
import model

load_dotenv()



LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
LINE_USER_ID = os.environ.get("LINE_USER_ID")
DEVICE_AUTH_TOKEN = os.environ.get("DEVICE_AUTH_TOKEN")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
geolocator = Nominatim(user_agent="geoapiExercises")



app = Flask(__name__)

# https://api.line.me/v2/bot/message/multicast
# https://api.line.me/v2/bot/message/broadcast
def send_reminder():
    user_id = LINE_USER_ID
    message = '記得要關心長輩哦！'
    line_bot_api.push_message(user_id, TextSendMessage(text=message))

scheduler = BackgroundScheduler()
# scheduler.add_job(send_reminder, 'interval', seconds=4)
scheduler.start()

@app.route("/notification", methods=['POST'])
def receive_fall_notification():
    body = request.get_data(as_text=True)                    # 取得收到的訊息內容
    try:
        location_data = json.loads(body)                         # json 格式化訊息內容
        print(location_data)
        location = geolocator.reverse(f"{location_data['V1']},{location_data['V0']}")
        user_id = LINE_USER_ID
        line_bot_api.push_message(user_id, LocationSendMessage(title="位置資訊", address=location.address, longitude=location_data['V0'], latitude=location_data['V1']))
    except Exception as e:
        print(f'Exception occurred: {e}')
        print(body)
    return 'OK'                                              # 驗證 Webhook 使用，不能省略

emoji_from_elder_count = 0
emoji_from_me_count = 0



@app.route("/heart_rate", methods=['POST'])
def receive_heart_rate_notification():
    body = request.get_data(as_text=True)                    # 取得收到的訊息內容
    try:
        location_data = json.loads(body)                         # json 格式化訊息內容
        print(location_data)
        location = geolocator.reverse(f"{location_data['V1']},{location_data['V0']}")
        user_id = LINE_USER_ID
        line_bot_api.push_message(user_id, LocationSendMessage(title="位置資訊", address=location.address, longitude=location_data['V0'], latitude=location_data['V1']))
    except Exception as e:
        print(f'Exception occurred: {e}')
        print(body)
    return 'OK' 



@app.route("/arduino_get", methods=['GET'])
def arduino_get():
    print('OK')
    return 'OK'

@app.route("/arduino_post", methods=['POST'])
def arduino_post():
    body = request.get_data(as_text=True)
    json_data = json.loads(body)
    print(json_data)
    return 'OK'




@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)
    try:
        json_data = json.loads(body)
        print(json_data)
        signature = request.headers['X-Line-Signature']      # 加入回傳的 headers
        handler.handle(body, signature)                      # 綁定訊息回傳的相關資訊
        tk = json_data['events'][0]['replyToken']            # 取得回傳訊息的 Token
        type = json_data['events'][0]['message']['type']     # 取得 LINE 收到的訊息類型
        if type == 'text':
            user_id = json_data['events'][0]['source']['userId']
            message_content = json_data['events'][0]['message']['text']
            reply = model.write_text_message(user_id, message_content)
            # if msg == '位置':
            #     response = requests.get(f"https://blynk.cloud/external/api/get?token={DEVICE_AUTH_TOKEN}&V0&V1")
            #     # print(f'response: {response.content}')
            #     if response.status_code == 200:
            #         location_data = json.loads(response.text)
            #         # print(f"{location_data['V1']},{location_data['V0']}")
            #         location = geolocator.reverse(f"{location_data['V1']},{location_data['V0']}")
            #         # print(location.address)
            #         line_bot_api.reply_message(tk, LocationSendMessage(title="位置資訊", address=location.address, longitude=location_data['V0'], latitude=location_data['V1']))
            #     else:
            #         reply = "無法獲取位置資訊"
            #         line_bot_api.reply_message(tk, TextSendMessage(reply))# 回傳訊息
            # else:
            # line_bot_api.reply_message(tk, TextSendMessage(reply))
        elif type == 'image':
            user_id = json_data['events'][0]['source']['userId']
            message_id = json_data['events'][0]['message']['id']

            message_content = line_bot_api.get_message_content(message_id)
            image_bytes = message_content.content
            # reply = model.write_image_message(image_bytes, user_id)
            # line_bot_api.reply_message(tk, TextSendMessage(reply))
        else:
            reply = '你傳的不是文字呦～'
            print(reply)
            # line_bot_api.reply_message(tk, TextSendMessage(reply))
    except Exception as e:
        print(f'Exception occurred: {e}')
        print(body)
        return '403'
    return 'OK'                                              # 驗證 Webhook 使用，不能省略


# @handler.add(MessageEvent)
# def handle_message(event):
#     user_id = event.source.userId
#     if user_profile_state == 'finished':
#         pass

#     user_profile_state = 
#     user_profiles[user_id] = {'stage': 'ask_name'}
user_states = {}
flex_message = requests.get('https://firebasestorage.googleapis.com/v0/b/openhci-880b9.appspot.com/o/default%2Ftemplate.json?alt=media&token=9361223b-fa27-4512-b865-cf92650c7265').json()
flex_message2 = requests.get('https://firebasestorage.googleapis.com/v0/b/openhci-880b9.appspot.com/o/default%2Ftemplate.json?alt=media&token=f27b2250-bd2f-47b9-a08a-98a0556e8594').json()

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print('handle message')
    # print(flex_message)
    text = event.message.text
    user_id = event.source.user_id
    if user_id not in user_states:
        user_states[user_id] = 'IDLE'

    if user_states[user_id] == 'IDLE':
        # model.write_elder_name(text, user_id)
        line_bot_api.reply_message(
            event.reply_token,
            messages=ImageSendMessage(
                original_content_url=r'https://firebasestorage.googleapis.com/v0/b/openhci-880b9.appspot.com/o/default%2F2.png?alt=media&token=b223dd37-f766-4b81-ba13-cd0530341fb0',
                preview_image_url=r'https://firebasestorage.googleapis.com/v0/b/openhci-880b9.appspot.com/o/default%2F2.png?alt=media&token=b223dd37-f766-4b81-ba13-cd0530341fb0'    
            )
        )
        user_states[user_id] = 'GET_NICKNAME'
    elif user_states[user_id] == 'GET_NICKNAME':
        # model.write_user_nickname(text, user_id)
        line_bot_api.reply_message(
            event.reply_token,
            messages=FlexSendMessage(alt_text="flex-message", contents=flex_message))
        user_states[user_id] = 'GET_ELDER_PHONE'
    elif user_states[user_id] == 'GET_ELDER_PHONE':
        
        # model.write_elder_phone()
        user_states[user_id] = 'GET_USER_BIRTHDAY'
    elif user_states[user_id] == 'GET_USER_BIRTHDAY':
        # model.write_user_birthday()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"""
感謝你填寫基本資料！
現在，來試試看發送一張照片或一段溫暖的文字給親人吧！讓他們感受到你的關心！

請於下方/拍照/傳送照片/傳送文字
        """)
        )
        user_states[user_id] = 'DONE'



@handler.add(FollowEvent)
def handle_follow(event):
    try:
        user_profile = line_bot_api.get_profile(event.source.user_id)
        user_name = user_profile.display_name
    except Exception as e:
        print(f"Error getting user profile: {e}")
        user_name = "朋友"

    welcome_message = f"""親愛的 {user_name}，
你願意花一點時間，給親愛的家人傳送一張照片和一句溫暖的話嗎？無論是一張日常生活的照片，還是一句簡單的關心，都能讓他們感受到你的愛與關懷
用你的心意，讓每一天都充滿溫情！

你可以把這個聊天室當作和長輩們互動的地方~ 直接傳送照片到這個聊天室，照片就會在長輩日曆播放囉！有什麼想跟長輩講的小叮嚀也可以直接在這裡輸入！希望能透過這小小的聊天室與日曆，溫暖你們的每一天~"""


    text_message = TextSendMessage(text=welcome_message)
    image_message = ImageSendMessage(
        original_content_url=r"https://firebasestorage.googleapis.com/v0/b/openhci-880b9.appspot.com/o/default%2F1.png?alt=media&token=1a1a2a84-fbf9-414b-a4b7-0b47fc59f213",
        preview_image_url=r"https://firebasestorage.googleapis.com/v0/b/openhci-880b9.appspot.com/o/default%2F1.png?alt=media&token=1a1a2a84-fbf9-414b-a4b7-0b47fc59f213"
    )
    line_bot_api.reply_message(
        event.reply_token,
        messages=[text_message, image_message]
    )


#     sign_up_user(event.source.userId)

# def sign_up_user(user_id):
#     user_profiles = {}
#     user_profile_state = 'ask_name'
#     profile['name'] = text
#     profile['stage'] = 'ask_nickname'
#     line_bot_api.reply_message(
#         event.reply_token,
#         TextSendMessage(text="你想被如何稱呼？")
#     )

#     model.sign_up_user(user_id)

@handler.add(PostbackEvent)
def handle_postback(event):
    try:
        data = event.postback.data
        # data = querystring.parse(event.postback.data)
        print('postback event')
        # print(event)
        user_id = event.source.user_id
        if data == 'store_time':
            time_string = event.postback.params['time']
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"你選擇的時間是：{time_string}")
            )
        elif data == 'not_provide_phone':
            print('not_provide_phone')
            line_bot_api.push_message(
                to=user_id,
                messages=FlexSendMessage(alt_text="flex-message2", contents=flex_message2)
            )
            # user_states[user_id] = 'GET_ELDER_PHONE'
        elif data == 'provide_phone':
            print('provide_phone')
            line_bot_api.push_message(
                to=user_id,
                messages=TextSendMessage(text="請於下方輸入親人連絡電話並傳送"))
        elif data == 'not_provide_birthday':
            line_bot_api.push_message(
                to=user_id,
                messages=
                TextSendMessage(text=f"""
感謝你填寫基本資料！
現在，來試試看發送一張照片或一段溫暖的文字給親人吧！讓他們感受到你的關心！

請於下方/拍照/傳送照片/傳送文字
            """)
            )
            # user_states[user_id] = 'DONE'
        elif data == 'provide_birthday':
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"""
請於下方輸入你的生日並傳送
            """)
            )
    except Exception as e:
        print(f'exception: {e}')


def send_time_quick_reply(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text='請選擇一個選項：',
            quick_reply=QuickReply(items=[
                QuickReplyButton(action=MessageAction(label="確認", text="確認")),
                QuickReplyButton(action=MessageAction(label="取消", text="取消")),
                QuickReplyButton(action=DatetimePickerAction(label="選擇時間", data="store_time", mode="time")),
            ])
        )
    )


if __name__ == "__main__":
  app.run(debug=True)




# /users
#    /userId {LINE Bot userId}
#    /name
#    /avatar

# /messages
#   /messageId
#      /content {text/imageURL}
#      /from {userId}
#      /timestamp