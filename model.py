import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime, timedelta
import os
import base64
import json
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import UnfollowEvent, ImageMessage, AudioSendMessage,  MessageEvent, TextMessage, ImageSendMessage, FlexSendMessage, FollowEvent, PostbackEvent, TextSendMessage, LocationSendMessage, QuickReply, QuickReplyButton, MessageAction, DatetimePickerAction



LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def send_audio(url):
    print('send audio')
    users = fetch_all_users()
    for user_id, user_data in users.items():
        if user_id:
            line_bot_api.push_message(
                user_id, 
                [TextSendMessage(text="阿嬤傳來了語音訊息！"), AudioSendMessage(original_content_url=url)]
            )


FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY")
FIREBASE_AUTH_DOMAIN = os.environ.get("FIREBASE_AUTH_DOMAIN")
FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID")
FIREBASE_STORAGE_BUCKET = os.environ.get("FIREBASE_STORAGE_BUCKET")
FIREBASE_MESSAGING_SENDER_ID = os.environ.get("FIREBASE_MESSAGING_SENDER_ID")
FIREBASE_APP_ID = os.environ.get("FIREBASE_APP_ID")
FIREBASE_MEASUREMENT_ID = os.environ.get("FIREBASE_MEASUREMENT_ID")
FIREBASE_DATABASE_URL = os.environ.get("FIREBASE_DATABASE_URL")

KEY_TYPE = os.environ.get("KEY_TYPE")
KEY_PROJECT_ID = os.environ.get("KEY_PROJECT_ID")
KEY_PRIVATE_KEY_ID = os.environ.get("KEY_PRIVATE_KEY_ID")
KEY_PRIVATE_KEY = os.environ.get("KEY_PRIVATE_KEY")
KEY_CLIENT_EMAIL = os.environ.get("KEY_CLIENT_EMAIL")
KEY_CLIENT_ID = os.environ.get("KEY_CLIENT_ID")
KEY_AUTH_URI = os.environ.get("KEY_AUTH_URI")
KEY_TOKEN_URI = os.environ.get("KEY_TOKEN_URI")
KEY_PROVIDER_CERT_URL = os.environ.get("KEY_PROVIDER_CERT_URL")
KEY_CLIENT_CERT_URL = os.environ.get("KEY_CLIENT_CERT_URL")
KEY_UNIVERSE_DOMAIN = os.environ.get("KEY_UNIVERSE_DOMAIN")
GOOGLE_APPLICATION_CREDENTIALS_BASE64 = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_BASE64')

firebase_config = { 
"apiKey": FIREBASE_API_KEY,
"authDomain": FIREBASE_AUTH_DOMAIN, 
"projectId": FIREBASE_PROJECT_ID, 
"storageBucket": FIREBASE_STORAGE_BUCKET,
"messagingSenderId": FIREBASE_MESSAGING_SENDER_ID ,
"appId": FIREBASE_APP_ID,
"measurementId": FIREBASE_MEASUREMENT_ID,
"databaseURL": FIREBASE_DATABASE_URL}

KEY = {
    "type": KEY_TYPE,
  "project_id": KEY_PROJECT_ID,
  "private_key_id": KEY_PRIVATE_KEY_ID,
  "private_key": KEY_PRIVATE_KEY,
  "client_email": KEY_CLIENT_EMAIL,
  "client_id": KEY_CLIENT_ID,
  "auth_uri": KEY_AUTH_URI,
  "token_uri": KEY_TOKEN_URI,
  "auth_provider_x509_cert_url": KEY_PROVIDER_CERT_URL,
  "client_x509_cert_url": KEY_CLIENT_CERT_URL,
  "universe_domain": KEY_UNIVERSE_DOMAIN
}

key_base64 = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_BASE64')
key_json = base64.b64decode(key_base64).decode()
key_dict = json.loads(key_json)

cred = credentials.Certificate(key_dict)
firebase_admin.initialize_app(cred, firebase_config)

root_ref = db.reference('/')

def can_send_message(user_id, message_type):
    today = datetime.now().strftime("%Y-%m-%d")
    user_ref = root_ref.child('users').child(user_id)
    last_sent_date = user_ref.child(message_type + '_last_sent').get()
    if last_sent_date == today:
        return False
    else:
        user_ref.child(message_type + '_last_sent').set(today)
        return True


def write_text_message(user_id, message_content):
    timestamp_str = datetime.now().strftime('%Y-%m-%d')
    messages_ref = root_ref.child(f'text_messages/{timestamp_str}')
    messages_ref.push({
        'from': user_id,
        'from_name': read_user_nickname(user_id),
        'content': message_content,
    })

def write_image_message(image_bytes, user_id):
    timestamp_str = datetime.now().strftime('%Y-%m-%d')
    file_name = f"{user_id}_{timestamp_str}.jpg"
    bucket = storage.bucket()
        
    blob = bucket.blob("images/" + file_name)
    blob.upload_from_string(image_bytes, content_type='image/jpeg')
    blob.make_public()
    image_url = blob.public_url
    
    
    messages_ref = root_ref.child(f'image_messages/{timestamp_str}')
    messages_ref.push({
        'from': user_id,
        'content': image_url,
    })

def write_elder_name(elder_name, user_id):
    print(f"write elder name")
    ref = root_ref.child(f'users/{user_id}/elderName')
    ref.set(elder_name)

def write_user_nickname(nickname, user_id):
    ref = root_ref.child(f'users/{user_id}/nickName')
    ref.set(nickname)

def write_elder_phone(elder_phone, user_id):
    ref = root_ref.child(f'users/{user_id}/elderPhone')
    ref.set(elder_phone)

def write_user_birthday(birthday, user_id):
    print('write user birthday')
    ref = root_ref.child(f'users/{user_id}/birthday')
    ref.set(birthday)

def update_user_text_message_count(user_id):
    ref = db.reference(f'users/{user_id}/text_messages_count')
    
    # Try to get the current count
    try:
        old_data = ref.get()
        print("old data: ", old_data)
        
        if old_data is None:
            old_data = 0
        new_data = int(old_data) + 1
        
        # Update the count in the database
        ref.set(new_data)
        print(f"Updated text_messages_count to {new_data} for user {user_id}")
    except Exception as e:
        print(f"Failed to update text_messages_count for user {user_id}: {e}")

def update_user_image_message_count(user_id):
    ref = db.reference(f'users/{user_id}/image_messages_count')
    
    # Try to get the current count
    try:
        old_data = ref.get()
        print("old data: ", old_data)
        
        if old_data is None:
            old_data = 0
        new_data = int(old_data) + 1
        
        # Update the count in the database
        ref.set(new_data)
        print(f"Updated image_messages_count to {new_data} for user {user_id}")
    except Exception as e:
        print(f"Failed to update image_messages_count for user {user_id}: {e}")

def read_user_nickname(user_id):
    ref = root_ref.child(f'users/{user_id}/nickName')
    return str(ref.get()) or False

def read_elder_name(user_id):
    ref = root_ref.child(f'users/{user_id}/elderName')
    return str(ref.get()) or False

def read_elder_phone(user_id):
    ref = root_ref.child(f'users/{user_id}/elderPhone')
    return str(ref.get()) or False

def read_user_nickname(user_id):
    ref = root_ref.child(f'users/{user_id}/nickName')
    return str(ref.get()) or False

def read_text_messages_count(user_id):
    try:
        ref = root_ref.child(f'users/{user_id}/text_messages_count')
        data = ref.get()
        if data is not None: 
            return int(data) 
        else:
            return 0 
    except Exception as e:
        print(f"Error reading text messages count for user {user_id}: {e}")
        return False 

def read_image_messages_count(user_id):
    try:
        ref = root_ref.child(f'users/{user_id}/image_messages_count')
        data = ref.get()
        if data is not None: 
            return int(data)
        else:
            return 0 
    except Exception as e:
        print(f"Error reading image messages count for user {user_id}: {e}")
        return False 

def write_user(user_id, user_name):
    try:
        users_ref = root_ref.child(f'users/{user_id}')
        users_ref.set({
            "name": user_name,
        })
        print(f"User {user_id} updated successfully.")
    except Exception as e:
        print(f"Failed to write user {user_id}: {e}")

def delete_user(user_id):
    try:
        ref = db.reference(f'users/{user_id}')
        ref.delete()
        print(f"User {user_id} deleted successfully.")
    except Exception as e:
        print(f"Error deleting user {user_id}: {e}")
        return False 

def fetch_all_users():
    try:
        ref = db.reference('users')
        return ref.get()
    except Exception as e:
        print(f"Error fetching all users: {e}")
        return False 


def update_user_state(user_id, state):
    try:
        ref = db.reference(f'users/{user_id}/state')
        ref.set(state)
    except Exception as e:
        print(f'Error updating user state {user_id}: {e}')


def read_user_state(user_id):
    try:
        ref = db.reference(f'users/{user_id}/state')
        return ref.get()
    except Exception as e:
        print(f'Error fetching user state {user_id}: {e}')



def update_date():
    date_ref = db.reference('date')
    torn_ref = db.reference('torn')
    
    try:
        old_data = date_ref.get()
        print("old data: ", old_data)
        
        if old_data is None:
            old_data = "2024-07-06" 

        current_date = datetime.strptime(old_data, "%Y-%m-%d")
        next_date = current_date + timedelta(days=1)
        new_data = next_date.strftime("%Y-%m-%d")
        
        date_ref.set(new_data)
        print(f"Updated date to {new_data}")
        
        torn_ref.set(False)
        print("Updated torn to False")
    except Exception as e:
        print(f"Failed to update date or torn: {e}")

def write_torn(torn_to_write):
    torn_ref = db.reference('torn')
    
    try:
        torn_ref.set(torn_to_write)
        print(f"Updated torn to {torn_to_write}")
    except Exception as e:
        print(f"Failed to update date or torn: {e}")

def read_torn():
    try:
        torn_ref = db.reference('torn')
        return torn_ref.get()
    except Exception as e:
        print(f"Error fetching torn: {e}")


def read_date():
    try:
        ref = db.reference('date')
        return ref.get()
    except Exception as e:
        print(f"Error fetching date: {e}")
        return False 

def write_date_info(data):
    current_date = datetime.now().strftime('%Y-%m-%d')
    ref = db.reference(f'/date_info/{current_date}')
    ref.set(data)

    print(f"Data for {current_date} has been written to the database.")



audio_timestamp_str = datetime.now().strftime('%Y-%m-%d')
audio_reference_path = f'audio_messages/{audio_timestamp_str}'

def send_tear_notification():
    print("send tear")
    try:
        users = fetch_all_users()
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

def torn_listener(event):
    print("torn event")
    ref = db.reference("torn")
    data = ref.get()
    print(f'Read data: {data}')
    if data == True:
        send_tear_notification()

def audio_listener(event):
    print("audio message event")

    ref = db.reference(audio_reference_path)
    data = ref.get()
    print(f'Read data: {data}')
    send_audio(data)

db.reference(audio_reference_path).listen(audio_listener)
db.reference('torn').listen(torn_listener)

# /users
#    /userId {LINE Bot userId}
#        /name
#        /state
#        /elderName
#        /nickName
#        /elderPhone
#        /birthDay
#        /text_messages_count
#        /image_messages_count


#/image_messages
#    /2024-07-05
#       /image_id
#           /content [image_url]
#           /from [user_id]
#/text_messages
#    /2024-07-05
#       /text_id
#           /content
#           /from
#           /from_name
#/audio_messages
#    /2024-07-05
#        /audio_id
#           /content [audio_url]

#/date

#/date_info
#    /2024-07-05
#       /lunar_date
#       /week_day [一～日]
#       /ganzhi [甲辰]
#       /yi
#       /ji
#       /good_times
#       /jieqi [小暑]
#       /sha

#/torn [True/False]