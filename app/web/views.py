from flask import render_template
from . import bp


@bp.get('/')
def index():
    return render_template('index.html')


@bp.get('/login')
def login():
    return render_template('login.html')
