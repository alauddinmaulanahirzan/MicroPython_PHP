# Firebase Section
from firebase_admin import db
import firebase_admin
from firebase_admin import credentials
from google.cloud import storage
# Additional Section
import platform

class FirebaseHandler:
    def connectDB():
        databaseURL = "https://rpi-pico-default-rtdb.asia-southeast1.firebasedatabase.app/"
        cred = credentials.Certificate("rpi-pico-firebase-adminsdk.json")
        app = firebase_admin.initialize_app(cred,{'databaseURL':databaseURL})
        reference = db.reference("/")
        return reference