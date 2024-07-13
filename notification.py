import random
import model
import os
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import UnfollowEvent, ImageMessage, AudioSendMessage,  MessageEvent, TextMessage, ImageSendMessage, FlexSendMessage, FollowEvent, PostbackEvent, TextSendMessage, LocationSendMessage, QuickReply, QuickReplyButton, MessageAction, DatetimePickerAction


LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
LINE_USER_ID = os.environ.get("LINE_USER_ID")
DEVICE_AUTH_TOKEN = os.environ.get("DEVICE_AUTH_TOKEN")
BLYNK_AUTH_TOKEN = 'moOCYh7P3Am3mKOLJRdBKOb1AkcesosW'
BLYNK_SERVER = 'blynk.cloud'
BLYNK_PIN = 'v0'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

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


def send_notification_message():
    print("send notification message")
    users = model.fetch_all_users()
    for user_id, user_data in users.items():
        user_nickname = user_data.get('nickName')
        elder_name = user_data.get('elderName')
        message = random_notification_message(user_nickname, elder_name)
        line_bot_api.push_message(user_id, TextSendMessage(text=message))

def send_no_tear_notification():
    print("send no tear")
    try:
        users = model.fetch_all_users()
        for user_id, user_data in users.items():
            user_nickname = user_data.get('nickName')
            elder_name = user_data.get('elderName')
        if user_id:
            line_bot_api.push_message(
                    user_id, 
                    TextSendMessage(text=f"嗨，{user_nickname}！\n我們注意到今天{elder_name}沒有與日曆互動。也許他今天有些忙碌，如果方便的話，抽空關心一下{elder_name}吧~確保他們一切都好！")
            )
    except LineBotApiError as e:
            print(f"Unexpected error: {e}")


def send_tear_notification():
    torn = model.read_torn()
    if torn == False:
        print("send tear")
        try:
            users = model.fetch_all_users()
            for user_id, user_data in users.items():
                user_nickname = user_data.get('nickName')
                elder_name = user_data.get('elderName')
                if user_id:
                    line_bot_api.push_message(
                        user_id, 
                        TextSendMessage(text=f"嗨！{user_nickname}，\n今天{elder_name}與日曆互動了！您的關心和分享讓他們每天都充滿喜悅。繼續保持這份互動，讓家人之間的感情更加親密吧！")
                    )
        except LineBotApiError as e:
            print(f"Unexpected error: {e}")