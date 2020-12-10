# -*- coding: utf-8 -*-
import hashlib
from flask import render_template, Blueprint, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from Blog.extensions import db
from Blog.form import LoginForm, RegisterForm, ForgetPasswordForm, ResetPasswordForm
from Blog.models import User
from Blog.emails import send_reset_password_email, send_confirm_email
from Blog.configs import Operations
from Blog.utils import redirect_back, generate_token, validate_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.validate_password(form.password.data):
            remember = form.remember.data
            print(user.role.name)
            login_user(user, remember)
            if not user.confirmed:
                return redirect(url_for('auth.unconfirmed'))
            flash('Login success.', 'info')
            return redirect_back()
        flash('Invalid email or password.', 'warning')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout success.', 'info')
    return redirect_back()

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        username = form.username.data
        password = form.password.data
        user = User(email=email, username=username)
        user.password=password
        token = generate_token(user=user, operation=Operations.CONFIRM)
        db.session.add(user)
        db.session.commit()
        send_confirm_email(user=user, token=token)
        flash('Register sucessfully. Please check your email and click the link to confirm your account.', 'info')
        return redirect(url_for('index.index'))
    return render_template('auth/register.html', form=form)


@auth_bp.route('/forget-password', methods=['GET', 'POST'])
def forget_password():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))

    form = ForgetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = generate_token(user=user, operation=Operations.RESET_PASSWORD)
            send_reset_password_email(user=user, token=token)
            flash('Password reset email sent, check your inbox.', 'info')
            return redirect(url_for('.login'))
        flash('Invalid email.', 'warning')
        return redirect(url_for('.forget_password'))
    return render_template('auth/reset_password.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is None:
            return redirect(url_for('.register'))
        if validate_token(token=token, operation=Operations.RESET_PASSWORD,
                          new_password=form.password.data):
            flash('Password updated.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid or expired link.', 'danger')
            return redirect(url_for('auth.forget_password'))
    return render_template('auth/reset_password.html', form=form)


@auth_bp.route('/confirm/<token>')
def confirm_account(token):
    message = validate_token(token=token, operation=Operations.CONFIRM)
    return render_template('auth/confirm.html',  message=message)


@auth_bp.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for('index.index'))
    # flash('Please confirm your account!', 'waring')
    return render_template('auth/unconfirmed.html', user=current_user)

@auth_bp.route('/resend')
def resend_confirmation():
    user = User.query.filter_by(email=current_user.email).first()
    token = generate_token(user=user, operation=Operations.CONFIRM)
    send_confirm_email(user=user, token=token)
    return redirect(url_for("auth.unconfirmed"))