from flask import Blueprint,render_template, request, current_app, flash, redirect, url_for, session
from flask_login import current_user
from Blog.models import Post, Category, Comment, User, Message
from Blog.utils import redirect_back, get_current_ip
from Blog.form import HelloForm
from Blog.extensions import db
from Blog.form import CommentForm
from Blog.emails import send_someone_connect_email

blog_bp = Blueprint('blog', __name__)

@blog_bp.route('/', methods=['GET', 'POST'])
def index():
	if current_user.is_authenticated:
		ip = get_current_ip()
		if ip != session.get('ip'):
			session['ip'] = get_current_ip()
			send_someone_connect_email('fanghao23@hotmail.com', ip)

	last = Post.query.order_by(Post.timestamp.desc()).first()
	form = HelloForm()
	if form.validate_on_submit():
		name = form.name.data
		body = form.body.data
		message = Message(body=body, name=name)
		db.session.add(message)
		db.session.commit()
		flash('Your message have been sent to the world!')
		return redirect(url_for('.index'))

	page = request.args.get('page', 1, type=int)
	per_page = current_app.config['MESSAGE_PER_PAGE']
	pagination = Message.query.order_by(Message.timestamp.desc()).paginate(page, per_page=per_page)
	messages = pagination.items

	return render_template('blog/index.html', post=last, pagination=pagination, messages=messages, form=form)

@blog_bp.route('/blog')
def blogs():
	page = request.args.get('page', 1, type=int)
	per_page = current_app.config['BLOG_POST_PER_PAGE']
	pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
	posts = pagination.items
	return render_template('blog/blog.html', pagination=pagination, posts=posts)

@blog_bp.route('/category/<int:category_id>', methods=['GET', 'POST'])
def categories(category_id):
	category = Category.query.get_or_404(category_id)
	page = request.args.get('page', 1, type=int)
	per_page = current_app.config['BLOG_POST_PER_PAGE']
	pagination = Post.query.filter_by(category_id=category_id).order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
	posts = pagination.items
	return render_template('blog/category.html', pagination=pagination, posts=posts, category=category)

@blog_bp.route('/blog/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
	post = Post.query.get_or_404(post_id)
	page = request.args.get('page', 1, type=int)
	per_page = current_app.config['BLOG_POST_PER_PAGE']
	pagination = Comment.query.filter_by(post_id=post_id).order_by(Comment.timestamp.desc()).paginate(
		page, per_page)
	comments = pagination.items
	form = CommentForm()
	if form.validate_on_submit():
		if current_user.is_authenticated:
			body = form.body.data
			author = current_user
			comment = Comment(body=body, post=post, author= author)
			replied_id = request.args.get('reply')
			if replied_id:
				replied_comment = Comment.query.get_or_404(replied_id)
				comment.replied = replied_comment
			db.session.add(comment)
			db.session.commit()
			return redirect(url_for('.show_post', post_id=post_id))
		else:
			flash('Please login first.', 'warning')
			return redirect(url_for('auth.login'))
	return render_template('blog/post.html', pagination=pagination, post=post, comments=comments, form=form)

@blog_bp.route('/reply/comment/<int:comment_id>')
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if not comment.post.can_comment:
        flash('Comment is disabled.', 'warning')
        return redirect(url_for('.show_post', post_id=comment.post.id))
    return redirect(
        url_for('.show_post', post_id=comment.post_id, reply=comment_id, author=comment.author.username) + '#comment-form')


@blog_bp.route('/search')
def search():
	q = request.args.get('q', '')
	if q == '':
		flash('Enter keyword about post, user or comment.', 'warning')
		return redirect_back()
	category = request.args.get('category', 'post')
	page = request.args.get('page', 1, type=int)
	per_page = current_app.config['BLOG_SEARCH_RESULT_PER_PAGE']
	if category == 'user':
		pagination = User.query.whooshee_search(q).paginate(page, per_page)
	elif category == 'comment':
		pagination = Comment.query.whooshee_search(q).paginate(page, per_page)
	else:
		pagination = Post.query.whooshee_search(q).paginate(page, per_page)
	results = pagination.items
	return render_template('blog/search.html', q=q, results=results, pagination=pagination, category=category)



