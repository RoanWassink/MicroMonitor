from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
Base = declarative_base()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    #posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# class Post(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     body = db.Column(db.String(140))
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#
#     def __repr__(self):
#         return '<Post {}>'.format(self.body)
#
#


class System(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    system_id = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    cpu_usage = db.Column(db.Float)
    cpu_temp = db.Column(db.Float)
    disk_free= db.Column(db.Float)
    disk_used= db.Column(db.Float)
    disk_percent = db.Column(db.Float)
    os = db.Column(db.String(140))
    cpu_cores_phys = db.Column(db.Integer)
    cpu_freq_max = db.Column(db.Float)
    memory_total = db.Column(db.Float)
    memory_used = db.Column(db.Float)
    memory_percent= db.Column(db.Float)

    def __repr__(self):
        return '{}'.format(self.system_id)






