# -*- coding: utf-8 -*-
import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev key')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = 587
    MAIL_USE_TSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('DEFAULT_SENDER')
    MAIL_SUBJECT_PREFIX = '[Fanco`s study room]'
    
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')

    BLOG_POST_PER_PAGE = 10
    BLOG_MANAGE_POST_PER_PAGE = 15
    BLOG_COMMENT_PER_PAGE = 15
    BLOG_SEARCH_RESULT_PER_PAGE = 15
    MESSAGE_PER_PAGE = 5
    WHOOSHEE_MIN_STRING_LEN = 3

    MAX_CONTENT_LENGTH = 3 * 1024 * 1024

    FILE_UPLOAD_PATH = os.path.join(basedir, 'uploads')
    IMAGE_UPLOAD_PATH = os.path.join(basedir, 'uploads/images')
    DROPZONE_ALLOWED_FILE_CUSTOM = True
    DROPZONE_ALLOWED_FILE_TYPE = 'image/*, .md, .txt'
    DROPZONE_MAX_FILE_SIZE = 3
    DROPZONE_MAX_FILES = 5
    DROPZONE_ENABLE_CSRF = True
    DROPZONE_DEFAULT_MESSAGE = ' Drop files here<br>Or<br><button type="button">Click to Upload</button>'

    DEBUG_TB_INTERCEPT_REDIRECTS = False

class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'data-dev.db')


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # in-memory database


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', prefix + os.path.join(basedir, 'data.db'))

class Operations:
    CONFIRM = 'confirm'
    RESET_PASSWORD = 'reset-password'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
