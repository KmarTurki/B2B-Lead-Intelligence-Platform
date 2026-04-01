import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

load_dotenv()

def init_firebase():
    cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH"))
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db
