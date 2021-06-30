import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth

firebase_admin.initialize_app(credentials.Certificate(os.environ.get('FIREBASE_ADMIN_SDK_KEY')))

def decode_token(id_token: str):
    decoded_token = auth.verify_id_token(id_token)
    return decoded_token
