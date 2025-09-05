from flask import Blueprint

bp = Blueprint('web', __name__)

from . import views  # noqa: F401
