from app.extensions import db
from app.models import Action, User


def log_action(action_type: str, user: User | None = None) -> Action:
    action = Action(action_type=action_type, user=user)
    db.session.add(action)
    db.session.commit()
    return action
