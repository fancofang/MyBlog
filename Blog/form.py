from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, ValidationError, TextAreaField, \
	HiddenField, DateField
from flask_pagedown.fields import PageDownField
from wtforms.validators import DataRequired,Length, Email, Regexp, EqualTo, Optional
from Blog.models import Category, User
from flask_ckeditor import CKEditorField

class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Length(1, 254), Email()])
	password = PasswordField('Password', validators=[DataRequired(), Length(1, 128)])
	remember = BooleanField('Remember me')
	submit = SubmitField('Log in')

class PostForm(FlaskForm):
	title = StringField('Title', validators=[DataRequired(), Length(1.128)])
	uploadtime = DateField('Uploadtime(Just valid on edit)', render_kw={'placeholder':"eg:1970-1-30"},validators=[Optional()])
	category = SelectField('Category', coerce=int, default=1)
	body = PageDownField('Body')
	submit = SubmitField('Submit')
	cancel = SubmitField('Cancel')

	def __init__(self, *args, **kwargs):
		super(PostForm, self).__init__(*args, **kwargs)
		self.category.choices = [(category.id, category.name) for category in Category.query.order_by(Category.name).all()]

class CategoryForm(FlaskForm):
	name = StringField('Category', validators=[DataRequired(), Length(1,20)])
	submit = SubmitField('Submit')

	def validate_name(self, field):
		if Category.query.filter_by(name=field.data).first():
			raise ValidationError('Name already in use.')

class CommentForm(FlaskForm):
	name = StringField('Nickname', validators=[DataRequired(), Length(1,20)])
	email = StringField("Email (* Required. If choose \"remember me\", then won't show again)", validators=[DataRequired(), Length(1, 254), Email()])
	body = TextAreaField('Comment', validators=[DataRequired()])
	remember = BooleanField('Remember me')
	be_reply = HiddenField('Replied')
	submit = SubmitField('Submit')
	
class CommentFormHidden(FlaskForm):
	name = HiddenField('Nickname', validators=[DataRequired(), Length(1,20)])
	email = HiddenField("Email", validators=[DataRequired(), Length(1, 254), Email()])
	body = TextAreaField('Comment', validators=[DataRequired()])
	be_reply = HiddenField('Replied')
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
	body = TextAreaField('Message', render_kw={'placeholder':"Appreciate share your comment or suggestion"}, validators=[DataRequired(), Length(1, 200)])
	submit = SubmitField('Send', render_kw={'id':"message_submit"})
	
class SettingForm(FlaskForm):
	username = StringField('Username', validators=[Length(1, 20),
												   Regexp('^[a-zA-Z][a-zA-Z0-9]*$',
														  message='The username should contain only a-z, A-Z, 0-9 and the initial letter must be alphabetic .')])
	image = StringField('Upload icon',validators=[Optional()])
	password = PasswordField('Password', render_kw={'placeholder':"如空白则默认不修改密码"}, validators=[Optional(), Length(8, 128), EqualTo('password2')])
	password2 = PasswordField('Confirm password', render_kw={'placeholder':"如空白则默认不修改密码"})
	submit = SubmitField()