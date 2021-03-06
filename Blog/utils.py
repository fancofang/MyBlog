# -*- coding: utf-8 -*-
try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

import os, uuid, re
from urllib.request import urlopen
from functools import wraps
from flask_login import current_user, login_user
from flask import request, redirect, url_for,current_app, abort
from itsdangerous import BadSignature, SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from Blog.models import User
from Blog.configs import Operations
from Blog.extensions import db

def rename_image(old_filename):
    ext = os.path.splitext(old_filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='index.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def generate_token(user, operation, expire_in=3600, **kwargs):
    s = Serializer(current_app.config['SECRET_KEY'], expire_in)

    data = {'id': user.id, 'operation': operation}
    data.update(**kwargs)
    user.token = s.dumps(data).decode('utf-8')
    db.session.commit()
    return s.dumps(data)


def validate_token(token, operation, new_password=None):
    s = Serializer(current_app.config['SECRET_KEY'])

    try:
        data = s.loads(token)
        user = User.query.filter_by(id=data.get('id')).first()
    except (SignatureExpired, BadSignature) as e:
        return "Token expired or does not match"
    
    if  user.token != token:
        return "Token was used."

    if operation == data.get('operation') and user:
        if operation == Operations.RESET_PASSWORD:
            user.password=new_password
            db.session.commit()
            return True
        elif operation == Operations.CONFIRM:
            user.set_role('USER')
            user.confirmed = True
            user.token = ""
            db.session.commit()
            return "Email confirmed sucessfully"
    else:
        return "Something wrong. Please do it again"

def permission_required(permission_name):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission_name):
                abort(403)
            return func(*args, **kwargs)
        return decorated_function
    return decorator

# def get_current_ip():
#     html = urlopen('http://checkip.dyndns.org/').read()
#     raw = html.decode('utf-8')
#     ip_addr = re.findall('\d+\.\d+\.\d+\.\d+', raw)
#     return ip_addr



