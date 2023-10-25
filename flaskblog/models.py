from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from datetime import datetime
from flask import current_app
from flaskblog import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    # This function will return a user by its id
    query = db.select(User).where(User.id == int(user_id))  # user_id should be an integer so int() here to be sure
    return db.session.execute(query).scalar()               # using scalar() to get only one element


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    password = db.Column(db.String(60),  nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self):
        s = Serializer(current_app.secret_key)
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.secret_key)
        try:
            user_id = s.loads(token, max_age=1800)['user_id']
        except Exception as er:
            print(er)
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
