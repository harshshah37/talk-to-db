import pyrebase
import openai
from google.cloud import bigquery
import bcrypt

# Firebase Configuration
firebase_config = {
    "apiKey": "AIzaSyCxhjec2NSSME1rXtS8bfUa4Anv0SfK_BM",
    "authDomain": "adt-project-ee49e.firebaseapp.com",
    "databaseURL": "https://adt-project-ee49e-default-rtdb.firebaseio.com",
    "projectId": "adt-project-ee49e",
    "storageBucket": "adt-project-ee49e.firebasestorage.app",
    "messagingSenderId": "298152423275",
    "appId": "1:298152423275:web:6cd85c9723843b3b8b662e",
    "measurementId": "G-DNYGN7YY9G"
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()

# Password hashing function
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
