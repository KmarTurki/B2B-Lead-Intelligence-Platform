from firebase_config import init_firebase

try:
    db = init_firebase()
    print("✅ Connected to Firebase Firestore successfully!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
