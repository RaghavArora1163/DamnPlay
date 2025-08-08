
import firebase_admin
from firebase_admin import credentials, db
import jwt
from flask import request, jsonify
from functools import wraps

firebase_app = None

def get_firebase_app():
    """
    Initialize Firebase if it hasn't been initialized yet.
    """
    global firebase_app
    if not firebase_app:
        cred = credentials.Certificate("C:/Users/RJ36/OneDrive/Desktop/RBAC Updated/user/firebase_credentials.json")
        firebase_app = firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://project-b15f4-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })
    return firebase_app

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('access-token')
        print(type(token))
        if not token:
            return jsonify({'error': 'Token is missing!'}), 401
        try:
            print(1)
            data = jwt.decode(token, "Raghav", algorithms=["HS256"])
            if data is None:
                print("missing")
            print(data)
            user_ref = db.reference(f'users/{data["user_id"]}').get()
            if not user_ref:
                raise ValueError("User not found")
            current_user = user_ref
            current_user['id'] = data["user_id"]  # Add user ID for reference in updates

        except Exception:
            return jsonify({'error': Exception }), 401
        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated
