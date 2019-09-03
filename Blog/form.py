from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, ValidationError, TextAreaField
from flask_pagedown.fields import PageDownField
from wtforms.validators import DataRequired,Length, Email, Regexp, EqualTo
from Blog.models import Category, User

class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Length(1, 254), Email()])
	password = PasswordField('Password', validators=[DataRequired(), Length(1, 128)])
	remember = BooleanField('Remember me')
	submit = SubmitField('Log in')

class PostForm(FlaskForm):
	title = StringField('Title', validators=[DataRequired(), Length(1.128)])
	category = SelectField('Category', coerce=int, default=1)
	body = PageDownField('Body', validators=[DataRequired()])
	submit = SubmitField('Submit')
	cancel = SubmitField('Cancel')

	def __init__(self, *args, **kwargs):
		super(PostForm, self).__init__(*args, **kwargs)
		self.category.choices = [(category.id, category.name) for category in Category.query.order_by(Category.name).all()]

class CategoryForm(FlaskForm):
	name = StringField('Category', validators=[DataRequired(), Length(1.20)])
	submit = SubmitField('Submit')

	def validate_name(self, field):
		if Category.query.filter_by(name=field.data).first():
			raise ValidationError('Name already in use.')

class CommentForm(FlaskForm):
	body = TextAreaField('Comment', validators=[DataRequired()])
	submit = SubmitField('Submit')

class RegisterForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Length(1, 254), Email()])
	username = StringField('Username', validators=[DataRequired(), Length(1, 20),
												   Regexp('^[a-zA-Z][a-zA-Z0-9]*$',
														  message='The username should contain only a-z, A-Z, 0-9 and the initial letter must be alphabetic .')])
	password = PasswordField('Password', validators=[
		DataRequired(), Length(8, 128), EqualTo('password2')])
	password2 = PasswordField('Confirm password', validators=[DataRequired()])
	submit = SubmitField()

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('The email is already in use.')

	def validate_username(self, field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError('The username is already in use.')

class ForgetPasswordForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Length(1, 254), Email()])
	submit = SubmitField()


class ResetPasswordForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Length(1, 254), Email()])
	password = PasswordField('Password', validators=[
		DataRequired(), Length(8, 128), EqualTo('password2')])
	password2 = PasswordField('Confirm password', validators=[DataRequired()])
	submit = SubmitField()


class HelloForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired(), Length(1, 20)])
	body = TextAreaField('Message', validators=[DataRequired(), Length(1, 200)])
	submit = SubmitField()