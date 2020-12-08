# -*- coding: utf-8 -*-
import requests
from threading import Thread

from flask import current_app, render_template
from flask_mail import Message

from Blog.extensions import mail


def _send_async_mail(app, message):
    print("sending email")
    print(app.config['MAIL_SERVER'])
    with app.app_context():
        mail.send(message)


def send_mail(to, subject, template, **kwargs):
    message = Message(current_app.config['MAIL_SUBJECT_PREFIX'] + subject, recipients=[to])
    message.body = render_template(template + '.txt', **kwargs)
    # message.html = render_template(template + '.html', **kwargs)
    app = current_app._get_current_object()
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
    return thr

def send_reset_password_email(user, token):
    send_mail(subject='Password Reset', to=user.email, template='emails/reset_password', user=user, token=token)


def send_confirm_email(user, token):
    send_mail(subject='Confirm email', to=user.email, template='emails/confirm_email', user=user, token=token)

# def send_comment_email(user, token):
#     send_mail(subject='Your post has a new comment', to=user.email, template='emails/reset_password', user=user, token=token)

def send_someone_connect_email(user_email, ip):
    send_mail(subject='Your website has a new visitor', to=user_email, template='emails/visitor_ip', ip=ip)


