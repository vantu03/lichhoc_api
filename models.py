# models.py
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<User {self.username} - {self.role}>"

class FcmToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User', backref='fcm_tokens')

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    expires_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref='tokens')

    def __repr__(self):
        return f"<Token {self.token[:10]}...>"

class FirebaseCredential(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    server_name = db.Column(db.String(50), unique=True, nullable=False)
    json_data = db.Column(db.Text, nullable=False)

class Feature(db.Model):
    __tablename__ = 'features'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    label = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(50), nullable=False, default='extension')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    details = db.relationship('FeatureDetail', backref='feature', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.key,
            'label': self.label,
            'icon': self.icon
        }

    def __repr__(self):
        return f"<Feature {self.key}>"

class FeatureDetail(db.Model):
    __tablename__ = 'feature_details'

    id = db.Column(db.Integer, primary_key=True)
    feature_id = db.Column(db.Integer, db.ForeignKey('features.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(100), nullable=True)
    payload = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'type': self.type,
            'title': self.title,
            **(json.loads(self.payload) if self.payload else {})
        }

    def __repr__(self):
        return f"<FeatureDetail type={self.type} for feature_id={self.feature_id}>"
