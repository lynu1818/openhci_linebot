import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

firebase_config = { 
"apiKey": "AIzaSyDX02z0txD8x1hsW2A-MC7KSh9aMY_gHtE",
"authDomain": "openhci-880b9.firebaseapp.com", 
"projectId": "openhci-880b9", 
"storageBucket": "openhci-880b9.appspot.com",
"messagingSenderId": "149604924509",
"appId": "1:149604924509:web:9bf171319ae99081b1a1b4",
"measurementId": "G-MNX51NYJJP",
"databaseURL": "https://openhci-880b9-default-rtdb.firebaseio.com/"}

cred = credentials.Certificate("key.json")
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
    timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
    messages_ref = root_ref.child('text_messages')
    messages_ref.push({
        'from': user_id,
        'content': message_content,
        'timestamp': timestamp_str
    })
    # reply = f'成功發送文字訊息！'
    # return reply

def write_image_message(image_bytes, user_id):
    timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"{user_id}_{timestamp_str}.jpg"
    bucket = storage.bucket()
        
    blob = bucket.blob("images/" + file_name)
    blob.upload_from_string(image_bytes, content_type='image/jpeg')
    image_url = blob.public_url
    
    messages_ref = root_ref.child('image_messages')
    messages_ref.push({
        'from': user_id,
        'content': image_url,
        'timestamp': timestamp_str
    })
    # reply = f'成功發送圖片訊息！'

    # return reply

def sign_up_user(user_id):
    users_ref = root_ref.child('users')