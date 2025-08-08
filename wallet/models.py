import firebase_admin
from firebase_admin import credentials, db
from user.models import get_firebase_app

# # Initialize Firebase Admin SDK
# cred = credentials.Certificate('firebase_key.json')  # Path to your service account key JSON
# firebase_admin.initialize_app(cred, {
#     'databaseURL': 'https://<your-database-name>.firebaseio.com/'  # Replace with your database URL
# })

get_firebase_app()

# Get a reference to the Realtime Database
def get_database_ref():
    return db.reference('wallets')
