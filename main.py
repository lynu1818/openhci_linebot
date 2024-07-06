from flask import Flask, request

import json

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import UnfollowEvent, ImageMessage, ButtonsTemplate, TemplateSendMessage, PostbackTemplateAction, MessageEvent, TextMessage, ImageSendMessage, FlexSendMessage, FollowEvent, PostbackEvent, TextSendMessage, LocationSendMessage, QuickReply, QuickReplyButton, MessageAction, DatetimePickerAction

import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from geopy.geocoders import Nominatim
import model
import random

load_dotenv()



def random_notification_message(user_nickname, elder_name) -> str:

    idx = random.randint(0, 2)

    if idx == 0:
        return f"""嗨{user_nickname}！
又是新的一天！別忘了抽空傳送一張照片或一句溫暖的話給{elder_name}。你的關心和問候對他們來說非常重要！可以讓他們感受到你的愛與陪伴(被愛emoji)
用小小的心意，點亮他們的每一天。
也祝你有個美好的一天！"""
    elif idx == 1:
        return f"""嗨{user_nickname}！
今天也是充滿愛的一天！快來和{elder_name}分享你的日常吧！傳一張有趣的照片或是一句暖心的話，讓他們感受到你的關懷和愛意吧！
小小的舉動，大大的溫暖！一起用愛心點亮每一天吧！
祝你今天也元氣滿滿！"""
    else:
        return f"""嗨，{user_nickname}！
今天又是和{elder_name}分享愛的好時機！快來傳一張有趣的照片或一句暖心的話，讓他們感受到你的關懷和思念吧！
你的每一份心意，都是他們的快樂泉源！一起用愛點亮他們的每一天吧！
祝你今天也充滿活力！"""



# TODO: 每到 00:00 從 database 檢查是否有撕日曆，若無則顯示前一日日期和照片
# TODO: 每日早上 8:00 提醒
def send_notification_message():
    users = model.fetch_all_users()
    for user_id, user_data in users.items():
        user_nickname = user_data.get('nickName')
        elder_name = user_data.get('elderName')
        message = random_notification_message(user_nickname, elder_name)
        line_bot_api.push_message(user_id, TextSendMessage(text=message))


# scheduler = BackgroundScheduler()
# scheduler.add_job(send_notification_message, 'cron', hour=10, minute=31)
# scheduler.start()


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


# def send_reminder():
#     user_id = LINE_USER_ID
#     message = '記得要關心長輩哦！'
#     line_bot_api.push_message(user_id, TextSendMessage(text=message))

# scheduler = BackgroundScheduler()
# scheduler.add_job(send_reminder, 'interval', seconds=4)
# scheduler.start()

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

# TODO: Maybe 接收撕日曆的訊號
@app.route("/arduino_post", methods=['POST'])
def arduino_post():
    body = request.get_data(as_text=True)
    json_data = json.loads(body)
    print(json_data)
    if json_data['done']:   # 有撕日曆
        line_bot_api.push_message() # 傳送給所有 user

        # maybe 紀錄有撕到 database
        # 更換螢幕顯示到今日的東西


    return 'OK'




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


user_states = {}
flex_message = requests.get('https://firebasestorage.googleapis.com/v0/b/openhci-880b9.appspot.com/o/default%2Ftemplate.json?alt=media&token=9361223b-fa27-4512-b865-cf92650c7265').json()
flex_message2 = requests.get('https://firebasestorage.googleapis.com/v0/b/openhci-880b9.appspot.com/o/default%2Ftemplate2.json?alt=media&token=6e60de93-c960-4dbb-ae6e-5ae05e52d799').json()

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    print('handle message')
    # print(flex_message)
    text = event.message.text
    user_id = event.source.user_id

    if user_id not in user_states:
        user_states[user_id] = 'IDLE'

    if user_states[user_id] == 'IDLE':
        model.write_elder_name(text, user_id)
        line_bot_api.reply_message(
            event.reply_token,
            messages=ImageSendMessage(
                original_content_url=r'https://firebasestorage.googleapis.com/v0/b/openhci-880b9.appspot.com/o/default%2F2.png?alt=media&token=b223dd37-f766-4b81-ba13-cd0530341fb0',
                preview_image_url=r'https://firebasestorage.googleapis.com/v0/b/openhci-880b9.appspot.com/o/default%2F2.png?alt=media&token=b223dd37-f766-4b81-ba13-cd0530341fb0'    
            )
        )
        user_states[user_id] = 'GET_NICKNAME'
    elif user_states[user_id] == 'GET_NICKNAME':
        model.write_user_nickname(text, user_id)
        line_bot_api.reply_message(
            event.reply_token,
            messages=FlexSendMessage(alt_text="flex-message", contents=flex_message))
        user_states[user_id] = 'GET_ELDER_PHONE'
    elif user_states[user_id] == 'GET_ELDER_PHONE':
        
        model.write_elder_phone(text, user_id)
        line_bot_api.push_message(
                user_id,
                messages=FlexSendMessage(alt_text="flex-message2", contents=flex_message2)
        )
        user_states[user_id] = 'GET_USER_BIRTHDAY'

    elif user_states[user_id] == 'GET_USER_BIRTHDAY':
        model.write_user_birthday(text, user_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"""感謝你填寫基本資料！
現在，來試試看發送一張照片或一段溫暖的文字給親人吧！讓他們感受到你的關心！
                            
請於下方/拍照/傳送照片/傳送文字""")
        )
        user_states[user_id] = 'DONE'
    elif user_states[user_id] == 'DONE':
        if(text == '到8:00了'):
            send_notification_message()
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
(點按及可通話)

本週累積關心訊息：{text_messages_count}天
用文字的力量，讓你們的心更近！"""))
    


@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    user_id = event.source.user_id

    if user_id not in user_states:
        user_states[user_id] = 'IDLE'
    
    if user_states[user_id] != 'DONE':
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
(點按及可通話)

本週累積上傳照片：{images_messages_count}天
太棒了！繼續保持這份關愛吧！"""))

@handler.add(UnfollowEvent)
def handle_unfollow(event):
    body = request.get_data(as_text=True)   
    try:
        user_id = event.source.user_id
        user_states[f'{user_id}'] = 'IDLE'
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


@handler.add(PostbackEvent)
def handle_postback(event):
    try:
        data = event.postback.data
        print('postback event')
        # print(event)
        user_id = event.source.user_id
        if data == 'not_provide_phone':
            print('not_provide_phone')
            line_bot_api.push_message(
                user_id,
                messages=FlexSendMessage(alt_text="flex-message2", contents=flex_message2)
            )
            user_states[user_id] = 'GET_USER_BIRTHDAY'
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
            user_states[user_id] = 'DONE'
        elif data == 'provide_birthday':
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"""請於下方輸入你的生日並傳送(ex. yyyy-mm-dd)""")
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
#        /name
#        /elderName
#        /nickName
#        /elderPhone
#        /birthDay
#        /text_messages_count
#        /image_messages_count