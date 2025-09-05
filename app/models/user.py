from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    username = db.Column(db.String, primary_key=True)
    password_hash = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True)
    role = db.Column(db.String, default='user')

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.username


@login_manager.user_loader
def load_user(username):
    return User.query.get(username)
