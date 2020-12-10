import hashlib
from datetime import date,datetime
from flask import current_app
from flask_login import UserMixin
from markdown2 import markdown
import random

from werkzeug.security import generate_password_hash, check_password_hash
from Blog.extensions import db, whooshee

@whooshee.register_model('username')
class User(db.Model, UserMixin):
	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(64), unique=True, index=True)
	username = db.Column(db.String(20), unique=True, index=True)
	password_hash = db.Column(db.String(128))
	image = db.Column(db.String(128))
	confirmed = db.Column(db.Boolean, default=False)
	token = db.Column(db.String(128))
	create_at = db.Column(db.DateTime, default=datetime.utcnow)

	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
	comments = db.relationship('Comment', backref='author')

	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		self.init_role()
		self.set_image()
		self.set_random_pass()

	@property
	def is_admin(self):
		return self.role.name == 'ADMIN'
	
	@property
	def is_guest(self):
		return self.role.name == 'GUEST'

	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	# @staticmethod
	# def init_role_permission():
	# 	for user in User.query.all():
	# 		if user.role is None:
	# 			if user.email == current_app.config['ADMIN_EMAIL']:
	# 				user.role = Role.query.filter_by(name='ADMIN').first()
	# 			else:
	# 				user.role = Role.query.filter_by(name='GUEST').first()
	# 		db.session.add(user)
	# 	db.session.commit()

	def validate_password(self, password):
		return check_password_hash(self.password_hash, password)
	
	def set_random_pass(self):
		s = [ random.choice('abcdefghijklmnopqrstuvwxyz!@#$%^&*()') for i in range(8)]
		self.password = "".join(s)
		db.session.commit()

	def init_role(self):
		if self.role is None:
			if self.email == current_app.config['ADMIN_EMAIL']:
				self.role = Role.query.filter_by(name='ADMIN').first()
				self.confirmed = True
			else:
				self.role = Role.query.filter_by(name='GUEST').first()
			db.session.commit()
			
	def set_role(self, name):
		if self.role.name != name.upper():
			self.role = Role.query.filter_by(name=name).first()
			db.session.commit()
			return True
		return False

	def set_image(self):
		if self.image is None:
			self.image = 'http://www.gravatar.com/avatar/%s?d=identicon&s=120' % hashlib.md5(self.email.encode('utf-8')).hexdigest()
			db.session.commit()


	def can(self, permission_name):
		permission = Permission.query.filter_by(name=permission_name).first()
		return permission is not None and self.role is not None and permission in self.role.permissions

roles_permissions = db.Table('roles_permissions',
							 db.Column('role_id', db.Integer, db.ForeignKey('roles.id')),
							 db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'))
							 )


class Permission(db.Model):
	__tablename__='permissions'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(30), unique=True)


class Role(db.Model):
	__tablename__ = 'roles'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(30), unique=True)
	default = db.Column(db.Boolean, default=False, index=True)
	users = db.relationship('User', backref='role', lazy='dynamic')
	permissions = db.relationship('Permission', secondary=roles_permissions, backref=db.backref('roles',lazy='dynamic'),lazy='dynamic')

	@staticmethod
	def init_role():
		roles_permissions_map = {
			# 'Locked': ['FOLLOW', 'COLLECT'],
			# 'User': ['FOLLOW', 'COLLECT', 'COMMENT', 'UPLOAD'],
			# 'Moderator': ['FOLLOW', 'COLLECT', 'COMMENT', 'UPLOAD', 'MODERATE'],
			# 'Administrator': ['FOLLOW', 'COLLECT', 'COMMENT', 'UPLOAD', 'MODERATE', 'ADMINISTER']
			'GUEST':[],
			'USER': ['COMMENT'],
			'ADMIN': ['COMMENT', 'ADMINISTER']
		}
		for role_name in roles_permissions_map:
			role = Role.query.filter_by(name=role_name).first()
			if role is None:
				role = Role(name=role_name)
				db.session.add(role)
			role.permissions = []
			for permission_name in roles_permissions_map[role_name]:
				permission = Permission.query.filter_by(name=permission_name).first()
				if permission is None:
					permission = Permission(name=permission_name)
					db.session.add(permission)
				role.permissions.append(permission)
		db.session.commit()

class Category(db.Model):
	__tablename__ = 'categorys'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(30), unique=True)

	posts = db.relationship('Post', backref='category')

	def delete(self):
		default_category = Category.query.get(1)
		posts = self.posts[:]
		for post in posts:
			post.category = default_category
		db.session.delete(self)
		db.session.commit()

@whooshee.register_model('title','body')
class Post(db.Model):
	__tablename__ = 'posts'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(60))
	body = db.Column(db.Text)
	body_html = db.Column(db.Text)
	timestamp = db.Column(db.Date, default=date.today, index=True)
	can_comment = db.Column(db.Boolean, default=True)

	category_id = db.Column(db.Integer, db.ForeignKey('categorys.id'))
	comments = db.relationship('Comment', backref='post', cascade='all, delete-orphan')

	def __init__(self, **kwargs):
		super(Post, self).__init__(**kwargs)
		self.set_category()

	def set_category(self):
		if self.category is None:
			self.category = Category.query.filter_by(name='Default').first()
			db.session.commit()

	@staticmethod
	def on_changed_body(target, value, oldvalue, initiator):
		# allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
		# 				'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
		# 				'h1', 'h2', 'h3', 'p']
		# target.body_html = bleach.linkify(bleach.clean(
		# 	markdown(value,extras=["tables"]),
		# 	tags=allowed_tags, strip=True))
		target.body_html = markdown(value,extras=["tables","fenced-code-blocks","code-color"])

db.event.listen(Post.body, 'set', Post.on_changed_body)

@whooshee.register_model('body')
class Comment(db.Model):
	__tablename__ = 'comments'

	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

	replied_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
	# replies = db.relationship('Comment', back_populates='replied', cascade='all')
	replies = db.relationship('Comment', back_populates='replied')
	replied = db.relationship('Comment', back_populates='replies', remote_side=[id])
	

class Message(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20))
	body = db.Column(db.String(100))
	timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)


