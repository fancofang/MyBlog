# -*- coding: utf-8 -*-
import flask_dropzone
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_whooshee import Whooshee
from flask_pagedown import PageDown
from flask_dropzone import Dropzone
from flask_migrate import Migrate

bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
mail = Mail()
moment = Moment()
whooshee = Whooshee()
pagedown = PageDown()
dropzone = Dropzone()
migrate = Migrate()




@login_manager.user_loader
def load_user(user_id):
    from Blog.models import User
    user = User.query.get(int(user_id))
    return user

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please login first'
login_manager.login_message_category = 'warning'
