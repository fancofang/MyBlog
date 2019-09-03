# -*- coding: utf-8 -*-

import random, hashlib
from faker import Faker
from sqlalchemy.exc import IntegrityError

from Blog import db
from Blog.models import User, Category, Post, Comment, Message

fake = Faker()


def fake_admin():
	admin = User(
		username='admin',
		email='admin@example.com',
		image = 'http://www.gravatar.com/avatar/%s?d=identicon&s=120' % hashlib.md5(random.choice('abcdefghijklmnopqrstuvwxyz!@#$%^&*()').encode('utf-8')).hexdigest()
	)
	admin.password = '12345678'
	db.session.add(admin)
	db.session.commit()

def fake_user(count=20):
	for i in range(count):
		users = User(
			username=fake.name(),
			email=fake.email(),
			image='http://www.gravatar.com/avatar/%s?d=identicon&s=120' % hashlib.md5(random.choice('abcdefghijklmnopqrstuvwxyz!@#$%^&*()').encode('utf-8')).hexdigest()
		)
		users.password = '12345678'
		db.session.add(users)
	db.session.commit()

def fake_categories(count=10):
	category = Category(name='Default')
	db.session.add(category)

	for i in range(count):
		category = Category(name=fake.word())
		db.session.add(category)
		try:
			db.session.commit()
		except IntegrityError:
			db.session.rollback()


def fake_posts(count=50):
	for i in range(count):
		post = Post(
			title=fake.sentence(),
			body=fake.text(2000),
			category=Category.query.get(random.randint(1, Category.query.count())),
			timestamp=fake.date_time_this_year()
		)

		db.session.add(post)
	db.session.commit()


def fake_comments(count=500):
	for i in range(count):
		comment = Comment(
			author=User.query.get(random.randint(1, User.query.count())),
			body=fake.sentence(),
			timestamp=fake.date_time_this_year(),
			post=Post.query.get(random.randint(1, Post.query.count()))
		)
		db.session.add(comment)
		db.session.commit()

	salt = int(count * 0.1)
	for i in range(salt):
		comment = Comment(
			body=fake.sentence(),
			timestamp=fake.date_time_this_year(),
			replied=Comment.query.get(random.randint(1, Comment.query.count())),
			post=Post.query.get(random.randint(1, Post.query.count())),
			author=User.query.get(random.randint(1, User.query.count()))
		)
		db.session.add(comment)
	db.session.commit()

def fake_messages(count=20):
	for i in range(count):
		message = Message(
			name=fake.name(),
			body=fake.sentence(),
			timestamp=fake.date_time_this_year(),
		)
		db.session.add(message)
	db.session.commit()


