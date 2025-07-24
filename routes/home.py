# routes/home.py
from flask import Blueprint, render_template
from models import FirebaseCredential, FcmToken

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def home():
    firebase_credentials = FirebaseCredential.query.all()
    tokens = [t.token for t in FcmToken.query.all()]
    return render_template('home.html', tokens=tokens, firebase_credentials=firebase_credentials)

@home_bp.route('/ping')
def ping():
    return "Server is alive"
