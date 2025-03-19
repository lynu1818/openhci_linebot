import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import datetime
import base64
import json

FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY")
FIREBASE_AUTH_DOMAIN = os.environ.get("FIREBASE_AUTH_DOMAIN")
FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID")
FIREBASE_STORAGE_BUCKET = os.environ.get("FIREBASE_STORAGE_BUCKET")
FIREBASE_MESSAGING_SENDER_ID = os.environ.get("FIREBASE_MESSAGING_SENDER_ID")
FIREBASE_APP_ID = os.environ.get("FIREBASE_APP_ID")
FIREBASE_MEASUREMENT_ID = os.environ.get("FIREBASE_MEASUREMENT_ID")
FIREBASE_DATABASE_URL = os.environ.get("FIREBASE_DATABASE_URL")

firebase_config = { 
"apiKey": FIREBASE_API_KEY,
"authDomain": FIREBASE_AUTH_DOMAIN, 
"projectId": FIREBASE_PROJECT_ID, 
"storageBucket": FIREBASE_STORAGE_BUCKET,
"messagingSenderId": FIREBASE_MESSAGING_SENDER_ID ,
"appId": FIREBASE_APP_ID,
"measurementId": FIREBASE_MEASUREMENT_ID,
"databaseURL": FIREBASE_DATABASE_URL}


key_base64 = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_BASE64')
key_json = base64.b64decode(key_base64).decode()
key_dict = json.loads(key_json)

cred = credentials.Certificate(key_dict)
firebase_admin.initialize_app(cred, firebase_config)

root_ref = db.reference('/')


# 上面的不用管(?)

# 錄完音呼叫這個 function
def upload_audio():
    timestamp_str = datetime.now().strftime('%Y-%m-%d')
    file_name = f"record.wav"       # 這個 firebase.py 檔案要放在 record.wav 同一層目錄下
    bucket = storage.bucket()
        
    blob = bucket.blob("audio/" + file_name)
    blob.upload_from_filename(filename=file_name, content_type="audio/wav")
    blob.make_public()
    audio_url = blob.public_url
    
    
    messages_ref = root_ref.child(f'audio_messages/{timestamp_str}')
    messages_ref.push({
        'content': audio_url,
    })



# 如果超音波測距距離大於某值可呼叫此 function（代表撕掉日曆），參數放 True，後面就不用管他了
def write_torn(torn_to_write : bool):
    torn_ref = db.reference('torn')
    
    try:
        torn_ref.set(torn_to_write)
        print(f"Updated torn to {torn_to_write}")
    except Exception as e:
        print(f"Failed to update date or torn: {e}")