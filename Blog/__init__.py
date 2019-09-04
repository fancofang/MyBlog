import os
import click
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import Flask,render_template, request
from flask_wtf.csrf import CSRFError
from Blog.blueprints.auth import auth_bp
from Blog.blueprints.blog import blog_bp
from Blog.blueprints.admin import admin_bp
from Blog.extensions import db, bootstrap, login_manager, csrf, mail, moment, whooshee, pagedown, dropzone, migrate, toolbar
from Blog.models import User, Post, Category, Comment, Permission, Role
from Blog.configs import config


basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('Blog')
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_commands(app)
    register_shell_context(app)
    register_errors(app)
    register_template_context(app)
    register_blueprints(app)
    register_logging(app)
    return app

def register_blueprints(app):
    app.register_blueprint(blog_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')


def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    whooshee.init_app(app)
    pagedown.init_app(app)
    dropzone.init_app(app)
    migrate.init_app(app, db)
    toolbar.init_app(app)


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(403)
    def page_forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(413)
    def request_too_large(e):
        return render_template('errors/413.html'), 413

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html', description=e.description), 400

def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, User=User, Post=Post, Category=Category, Comment=Comment, Permission=Permission, Role=Role)

def register_template_context(app):
    @app.context_processor
    def make_template_context():
        admin = User.query.filter_by(username='admin').first()
        categories = Category.query.order_by(Category.name).all()
        return dict(admin=admin, categories=categories)

def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database."""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    @click.option('--username', prompt=True, help='The username used to login.')
    @click.option('--password', prompt=True, hide_input=True,
                  confirmation_prompt=True, help='The password used to login.')
    def init(username, password):
        """Building Bluelog, just for you."""

        click.echo('Initializing the database...')
        db.create_all()

        admin = User.query.first()
        if admin is not None:
            click.echo('The administrator already exists, updating...')
            admin.username = username
            admin.password = password
        else:
            click.echo('Creating the temporary administrator account...')
            admin = User(
                username='admin',
                email='admin@example.com'
            )
            admin.password = password
            db.session.add(admin)

        category = Category.query.first()
        if category is None:
            click.echo('Creating the default category...')
            category = Category(name='Default')
            db.session.add(category)

        db.session.commit()
        click.echo('Done.')

    @app.cli.command()
    @click.option('--user', default=10, help='Quantity of users, default is 10.')
    @click.option('--category', default=10, help='Quantity of categories, default is 10.')
    @click.option('--post', default=50, help='Quantity of posts, default is 50.')
    @click.option('--comment', default=500, help='Quantity of comments, default is 500.')
    @click.option('--message', default=20, help='Quantity of messages, default is 20.')
    def forge(user, category, post, comment, message):
        """Generate fake data."""
        from Blog.fakes import fake_admin, fake_user, fake_categories, fake_posts, fake_comments, fake_messages

        db.drop_all()
        db.create_all()

        click.echo('Initializing the roles and permissions...')
        Role.init_role()

        click.echo('Generating the administrator...')
        fake_admin()

        click.echo('Generating %d the users...' % user)
        fake_user()

        click.echo('Generating %d categories...' % category)
        fake_categories(category)

        click.echo('Generating %d posts...' % post)
        fake_posts(post)

        click.echo('Generating %d comments...' % comment)
        fake_comments(comment)

        click.echo('Generating %d messages...' % message)
        fake_messages(message)

        click.echo('Done.')





def register_logging(app):
    class RequestFormatter(logging.Formatter):

        def format(self, record):
            record.url = request.url
            record.remote_addr = request.remote_addr
            return super(RequestFormatter, self).format(record)

    request_formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(os.path.join(basedir, 'logs/Blog.log'),
                                       maxBytes=10 * 1024 * 1024, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    mail_handler = SMTPHandler(
        mailhost=app.config['MAIL_SERVER'],
        fromaddr=app.config['MAIL_USERNAME'],
        toaddrs=['ADMIN_EMAIL'],
        subject='fancoblog Application Error',
        credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']))
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(request_formatter)

    if not app.debug:
        app.logger.addHandler(mail_handler)
        app.logger.addHandler(file_handler)