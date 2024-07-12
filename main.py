from flask import Flask, request

import json

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import UnfollowEvent, ImageMessage, AudioSendMessage,  MessageEvent, TextMessage, ImageSendMessage, FlexSendMessage, FollowEvent, PostbackEvent, TextSendMessage, LocationSendMessage, QuickReply, QuickReplyButton, MessageAction, DatetimePickerAction

import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import random
import time
import pytz
import model
import soup
import notification

load_dotenv()



tz = pytz.timezone('Asia/Taipei')

scheduler = BackgroundScheduler(timezone=tz)
scheduler.add_job(notification.send_notification_message, 'cron', hour=8, minute=0)
scheduler.add_job(soup.fetch_date_data, 'cron', hour=2, minute=30)
scheduler.add_job(model.write_torn, 'cron', hour=0, minute=0, args=[False])
scheduler.start()


LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
LINE_USER_ID = os.environ.get("LINE_USER_ID")
DEVICE_AUTH_TOKEN = os.environ.get("DEVICE_AUTH_TOKEN")
BLYNK_AUTH_TOKEN = 'moOCYh7P3Am3mKOLJRdBKOb1AkcesosW'
BLYNK_SERVER = 'blynk.cloud'
BLYNK_PIN = 'v0'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)



app = Flask(__name__)



@app.route("/arduino_get", methods=['GET'])
def arduino_get():
    print('OK')
    return 'OK'

receiving_audio = False

# TODO: Maybe 接收撕日曆的訊號
@app.route("/arduino_post", methods=['POST'])
def arduino_post():
    body = request.get_data(as_text=True)
    json_data = json.loads(body)
    print(json_data)
    if 'torn' in json_data:   # 有撕日曆訊號
        if json_data['torn'] == 1:
            notification.send_tear_notification()
            model.write_torn(True)
    if 'audio' in json_data:
        global receiving_audio
        if json_data['audio'] == 1 and receiving_audio == False:
            print('send audio')
            receiving_audio = True
            line_bot_api.broadcast([TextSendMessage(text="阿嬤傳來了語音訊息！"), AudioSendMessage(original_content_url=r'https://firebasestorage.googleapis.com/v0/b/openhci-880b9.appspot.com/o/default%2F%E9%98%BF%E5%AC%A4%E9%8C%84%E9%9F%B3.m4a?alt=media&token=d3cb71e4-735b-442a-9448-d2639f9df1de', duration=4000)])
        elif json_data['audio'] == 0 and receiving_audio == True:
            receiving_audio = False

    return 'OK'

def test_arduino_post():
    notification.send_tear_notification()
    model.write_torn(True)

#TODO: 加 emoji

@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)
    try:
        json_data = json.loads(body)
        print(json_data)
        signature = request.headers['X-Line-Signature']      # 加入回傳的 headers
        handler.handle(body, signature)  
    except Exception as e:
        print(f'Exception occurred: {e}')
        print(body)
        return '403'
    return 'OK'                                              # 驗證 Webhook 使用，不能省略


# TODO: 重傳 flex message 1
flex_message = requests.get('https://firebasestorage.googleapis.com/v0/b/openhci-880b9.appspot.com/o/default%2Ftemplate.json?alt=media&token=9361223b-fa27-4512-b865-cf92650c7265').json()
flex_message2 = requests.get('https://firebasestorage.googleapis.com/v0/b/openhci-880b9.appspot.com/o/default%2Ftemplate2.json?alt=media&token=6e60de93-c960-4dbb-ae6e-5ae05e52d799').json()
birthday_picker_action = DatetimePickerAction(
                label='選擇生日',
                data='birthday_picker',
                mode='date',  # 可以使用 'datetime' 來包含時間
                initial='',
                max='',
                min=''
            )
birthday_picker_flex_message = {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "請選擇你的生日日期",
                            "wrap": True
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "color": "#9E7148",
                            "action": birthday_picker_action
                        }
                    ]
                }
            }


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    print('handle message')
    text = event.message.text
    user_id = event.source.user_id

    user_state = model.read_user_state(user_id)

    if user_state == 'IDLE':
        model.write_elder_name(text, user_id)
        line_bot_api.reply_message(
            event.reply_token,
            messages=ImageSendMessage(
                original_content_url=r'https://firebasestorage.googleapis.com/v0/b/openhci-880b9.appspot.com/o/default%2F2.jpg?alt=media&token=cf1da200-7ae5-4b04-b149-48a68250479a',
                preview_image_url=r'https://firebasestorage.googleapis.com/v0/b/openhci-880b9.appspot.com/o/default%2F2.jpg?alt=media&token=cf1da200-7ae5-4b04-b149-48a68250479a'    
            )
        )
        model.update_user_state(user_id, 'GET_NICKNAME')
    elif user_state == 'GET_NICKNAME':
        model.write_user_nickname(text, user_id)
        line_bot_api.reply_message(
            event.reply_token,
            messages=FlexSendMessage(alt_text="flex-message", contents=flex_message))
        model.update_user_state(user_id, 'GET_ELDER_PHONE')
    elif user_state == 'GET_ELDER_PHONE':
        
        model.write_elder_phone(text, user_id)
        line_bot_api.push_message(
                user_id,
                messages=FlexSendMessage(alt_text="flex-message2", contents=flex_message2)
        )
        model.update_user_state(user_id, 'GET_USER_BIRTHDAY')

    elif user_state == 'GET_USER_BIRTHDAY':
        model.write_user_birthday(text, user_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"""感謝你填寫基本資料！
                            現在，來試試看發送一張照片或一段溫暖的文字給親人吧！讓他們感受到你的關心！
                            請於下方/拍照/傳送照片/傳送文字""")
        )
        model.update_user_state(user_id, 'DONE')
    elif user_state == 'DONE':
        try:
            torn = model.read_torn()
            if text == '到8:00了':
                notification.send_notification_message()
            elif text == '到12:00了':
                # blynk send message "on" for printer
                blynk_url = f'https://{BLYNK_SERVER}/external/api/update?token={BLYNK_AUTH_TOKEN}&{BLYNK_PIN}=1'
                requests.get(blynk_url)
                blynk_url = f'https://{BLYNK_SERVER}/external/api/update?token={BLYNK_AUTH_TOKEN}&{BLYNK_PIN}=0'
                requests.get(blynk_url)
                if not torn:
                    notification.send_no_tear_notification()
                model.update_date()
            elif text == '撕日曆':     # !!! for test
                test_arduino_post()
            else:
                model.write_text_message(user_id, text)
                model.update_user_text_message_count(user_id)
                elder_name = model.read_elder_name(user_id)
                elder_phone = model.read_elder_phone(user_id)
                text_messages_count = model.read_text_messages_count(user_id)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f"""文字傳輸成功！！

文字具有拉近心與心距離的力量。有空時，也請將這些溫暖化為語音，打個電話或親自探望{elder_name}吧！

{elder_phone}
(點按即可通話)

本週累積關心訊息：{text_messages_count}天
用文字的力量，讓你們的心更近！"""))
        except Exception as e:
            print(f'Exception : {e}')
    


@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    user_id = event.source.user_id

    user_state = model.read_user_state(user_id)
    
    if user_state != 'DONE':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"""請完成基本資料設定！""")
        )
    else:
        message_id = event.message.id

        message_content = line_bot_api.get_message_content(message_id)
        image_bytes = message_content.content
        model.write_image_message(image_bytes, user_id)
        model.update_user_image_message_count(user_id)
        elder_name = model.read_elder_name(user_id)
        elder_phone = model.read_elder_phone(user_id)
        images_messages_count = model.read_image_messages_count(user_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"""照片傳輸成功！！

{elder_name}又更了解你的日常了
相信{elder_name}收到一定很高興喔！
有時間也記得撥空打通電話或是與{elder_name}見個面吧！

{elder_phone}
(點按即可通話)

本週累積上傳照片：{images_messages_count}天
太棒了！繼續保持這份關愛吧！"""))

@handler.add(UnfollowEvent)
def handle_unfollow(event):
    body = request.get_data(as_text=True)   
    try:
        user_id = event.source.user_id
        model.delete_user(user_id)
    except Exception as e:
        print(f"Failed to handle unfollow event {user_id}: {e}")



@handler.add(FollowEvent)
def handle_follow(event):
    try:
        user_profile = line_bot_api.get_profile(event.source.user_id)
        print(user_profile)
        user_name = user_profile.display_name
        model.write_user(event.source.user_id, user_name)
        model.update_user_state(event.source.user_id, 'IDLE')
    except Exception as e:
        print(f"Error getting user profile: {e}")
        user_name = "朋友"

    welcome_message1 = f"""親愛的{user_name}，
今天願意花點時間傳送一張照片和一句溫暖的話給家人，讓他們感受到你的愛嗎？

你可以把這個聊天室當作與長輩互動的地方~ 傳送照片和留言到這裡，就會顯示在他們的日曆上。希望這小小的聊天室與日曆，能溫暖你們的每一天！"""
    welcome_message2 = r'請填寫基本資料$$'

    text_message1 = TextSendMessage(text=welcome_message1)
    text_message2 = TextSendMessage(text=welcome_message2, emojis=[{
        "index": 7,
        "productId": "5ac21a18040ab15980c9b43e",
        "emojiId": "003"
      },
      {
        "index": 8,
        "productId": "5ac21a18040ab15980c9b43e",
        "emojiId": "003"
      }])
    image_message = ImageSendMessage(
        original_content_url=r"https://firebasestorage.googleapis.com/v0/b/openhci-880b9.appspot.com/o/default%2F1.jpg?alt=media&token=5d3de029-4a61-4adb-bcf1-eb9a5ce5f181",
        preview_image_url=r"https://firebasestorage.googleapis.com/v0/b/openhci-880b9.appspot.com/o/default%2F1.jpg?alt=media&token=5d3de029-4a61-4adb-bcf1-eb9a5ce5f181"
    )
    line_bot_api.reply_message(
        event.reply_token,
        messages=[text_message1, text_message2, image_message]
    )


@handler.add(PostbackEvent)
def handle_postback(event):
    try:
        data = event.postback.data
        print('postback event')
        print(data)
        # print(event)
        user_id = event.source.user_id
        if data == 'not_provide_phone':
            print('not_provide_phone')
            line_bot_api.push_message(
                user_id,
                messages=FlexSendMessage(alt_text="flex-message2", contents=flex_message2)
            )
            model.update_user_state(user_id, 'GET_USER_BIRTHDAY')
        elif data == 'provide_phone':
            print('provide_phone')
            line_bot_api.push_message(
                user_id, 
                messages=TextSendMessage(text="請於下方輸入親人連絡電話並傳送(ex. 09xxxxxxxx)")) # TODO: 加家電
        elif data == 'not_provide_birthday':
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"""感謝你填寫基本資料！
現在，來試試看發送一張照片或一段溫暖的文字給親人吧！讓他們感受到你的關心！

請於下方/拍照/傳送照片/傳送文字""")
            )
            model.update_user_state(user_id, 'DONE')
        elif data == 'provide_birthday':
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(alt_text="選擇生日日期", contents=birthday_picker_flex_message)
            )
        elif data == 'birthday_picker':
            try:
                print(event.postback.params['date'])

                model.write_user_birthday(event.postback.params['date'], user_id)
                line_bot_api.push_message(
                    user_id,
                    TextSendMessage(text=f"""感謝你填寫基本資料！
現在，來試試看發送一張照片或一段溫暖的文字給親人吧！讓他們感受到你的關心！

請於下方/拍照/傳送照片/傳送文字""")
                )
                model.update_user_state(user_id, 'DONE')
            except Exception as e:
                print(f'Error processing birthday-picker: {e}')

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
    app.run(host="0.0.0.0", port=8080)
    # Ensure chromedriver has execute permissions
    os.chmod('./chromedriver_linux64/chromedriver', 0o755)
    soup.install_chrome()