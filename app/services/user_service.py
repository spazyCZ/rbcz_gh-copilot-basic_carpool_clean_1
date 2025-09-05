from app.extensions import db
from app.models import User


def get_by_username(username: str) -> User | None:
    return User.query.get(username)


def create_user(username: str, password: str, email: str | None = None, role: str = 'user') -> User:
    user = User(username=username, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user
