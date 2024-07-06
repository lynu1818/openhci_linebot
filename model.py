import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime, timedelta

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
        'from_name': read_user_nickname(user_id),
        'content': message_content,
        'timestamp': timestamp_str
    })
    # reply = f'成功發送文字訊息！'
    # return reply

def write_image_message(image_bytes, user_id):
    timestamp_str = read_date()
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
    # reply = f'成功發送圖片訊息！'

    # return reply

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
        ref = db.reference(f'users/{user_id}')
    except Exception as e:
        print(f'Error updating user state {user_id}: {e}')

def update_date():
    date_ref = db.reference('date')
    torn_ref = db.reference('torn')  # 新增对 torn 节点的引用
    
    try:
        old_data = date_ref.get()
        print("old data: ", old_data)
        
        if old_data is None:
            old_data = "2024-07-06"  # 默认日期

        current_date = datetime.strptime(old_data, "%Y-%m-%d")
        next_date = current_date + timedelta(days=1)
        new_data = next_date.strftime("%Y-%m-%d")
        
        date_ref.set(new_data)
        print(f"Updated date to {new_data}")
        
        torn_ref.set(False)  # 使用 update() 方法更新 torn 节点
        print("Updated torn to False")
    except Exception as e:
        print(f"Failed to update date or torn: {e}")

def write_torn():
    torn_ref = db.reference('torn')
    
    try:
        torn_ref.set(True)
        print("Updated torn to True")
    except Exception as e:
        print(f"Failed to update date or torn: {e}")

def read_date():
    try:
        ref = db.reference('date')
        return ref.get()
    except Exception as e:
        print(f"Error fetching date: {e}")
        return False 

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


# /text_messages
#   /messageId
#      /content {text/imageURL}
#      /from {userId}
#      /timestamp


# /image_messages
#   /messageId
#      /content {text/imageURL}
#      /from {userId}
#      /timestamp


# /date (for demo)
#    2024-07-06
# /torn
#    True or False