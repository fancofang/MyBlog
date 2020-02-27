import os
from datetime import datetime
from flask import Blueprint, flash, render_template, url_for, redirect, request, current_app
from flask_login import login_required, current_user
from Blog.form import PostForm, CategoryForm
from Blog.models import Category, Post, Comment, Message
from Blog.extensions import db
from Blog.utils import redirect_back, permission_required, rename_image

admin_bp = Blueprint('admin',__name__)

@admin_bp.before_request
@login_required
@permission_required('ADMINISTER')
def login_protect():
	pass


@admin_bp.route('/post/manage')
def manage_post():
	page = request.args.get('page', 1, type=int)
	pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
		page, per_page=current_app.config['BLOG_MANAGE_POST_PER_PAGE'])
	posts = pagination.items
	return render_template('admin/manage_post.html', page=page, pagination=pagination, posts=posts)

@admin_bp.route('/post/new', methods=['GET', 'POST'])
def new_post():
	form = PostForm()
	if form.validate_on_submit():
		title = form.title.data
		category = Category.query.get(form.category.data)
		body = form.body.data
		post = Post(title=title, body=body, category=category)
		db.session.add(post)
		db.session.commit()
		flash('Post created.', 'success')
		return redirect(url_for('blog.show_post', post_id=post.id))
	return render_template('admin/post.html', form=form)


@admin_bp.route('/post/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
	form = PostForm()
	post = Post.query.get_or_404(post_id)
	if form.validate_on_submit():
		if form.submit.data:
			post.title = form.title.data
			post.category = Category.query.get(form.category.data)
			print(post.timestamp)
			if form.uploadtime.data:
				post.timestamp = datetime.strptime(form.uploadtime.data, '%Y-%m-%d %H:%M:%S')
				print(post.timestamp)
			post.body = form.body.data
			db.session.commit()
			flash('Post is updated.', 'success')
		return redirect(url_for('blog.show_post', post_id=post.id))
	form.title.data = post.title
	form.body.data = post.body
	form.category.data = post.category_id
	return render_template('admin/post.html', form=form , post=post)

@admin_bp.route('/post/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	db.session.delete(post)
	db.session.commit()
	flash('Post is deleted.', 'success')
	return redirect_back()


@admin_bp.route('/category/manage')
def manage_category():
	categories = Category.query.all()
	return render_template('admin/manage_category.html', categories=categories)

@admin_bp.route('/category/new', methods=['GET', 'POST'])
def new_category():
	form = CategoryForm()
	if form.validate_on_submit():
		name = form.name.data
		if name != 'Default' :
			category = Category(name=name)
			db.session.add(category)
			db.session.commit()
			flash('Category updated.', 'success')
			return redirect(url_for('.manage_category'))
	return render_template('admin/category.html', form=form)


@admin_bp.route('/category/edit/<int:category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
	form = CategoryForm()
	category = Category.query.get_or_404(category_id)
	if category.id == 1:
		flash('You can not edit the default category.', 'warning')
		return redirect_back()
	if form.validate_on_submit():
		category.name = form.name.data
		db.session.commit()
		flash('Category updated.', 'success')
		return redirect(url_for('.manage_category'))

	form.name.data = category.name
	return render_template('admin/category.html', form=form)


@admin_bp.route('/category/delete/<int:category_id>', methods=['POST'])
def delete_category(category_id):
	category = Category.query.get_or_404(category_id)
	if category.id == 1:
		flash('You can not delete the default category.', 'warning')
		return redirect_back()
	category.delete()
	flash('Category deleted.', 'success')
	return redirect(url_for('.manage_category'))

@admin_bp.route('/comment/manage')
def manage_comment():
	page = request.args.get('page', 1, type=int)
	per_page = current_app.config['BLOG_COMMENT_PER_PAGE']
	pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(page, per_page=per_page)
	comments = pagination.items
	return render_template('admin/manage_comment.html', comments=comments, pagination=pagination)


@admin_bp.route('/comment/delete/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'success')
    return redirect_back()


@admin_bp.route('/post/set-comment/<int:post_id>', methods=['POST'])
def set_comment(post_id):
    post = Post.query.get_or_404(post_id)
    if post.can_comment:
        post.can_comment = False
        flash('Comment disabled.', 'success')
    else:
        post.can_comment = True
        flash('Comment enabled.', 'success')
    db.session.commit()
    return redirect_back()

@admin_bp.route('/message/manage')
def manage_message():
	page = request.args.get('page', 1, type=int)
	per_page = current_app.config['BLOG_COMMENT_PER_PAGE']
	pagination = Message.query.order_by(Message.timestamp.desc()).paginate(page, per_page=per_page)
	messages = pagination.items
	return render_template('admin/manage_message.html', messages=messages, pagination=pagination)

@admin_bp.route('/message/delete/<int:message_id>', methods=['POST'])
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    flash('Message deleted.', 'success')
    return redirect_back()


@admin_bp.route('/upload', methods=['GET', 'POST'])
def upload():
	if request.method == 'POST' and 'file' in request.files:
		f = request.files.get('file')
		filename = f.filename
		filetype = filename.split('.', 1)[1]
		if filetype in ['md','txt']:
			path = os.path.join(current_app.config['FILE_UPLOAD_PATH'], filename)
		else:
			path = os.path.join(current_app.config['IMAGE_UPLOAD_PATH'], filename)
		f.save(path)
		if filetype in ['md','txt']:
			with open(path, 'r', encoding='UTF-8', errors='ignore') as essay:
				s = essay.read()
				title = filename.split('.', 1)[0]
				new_post = Post(title=title,body=s)
				db.session.add(new_post)
				db.session.commit()
				print(s)
				print(title)
				print('successful!!!!!')
			# if Post.query.filter_by(title='title'):
			# 	print("ggggggggggg")
			# else:
			# 	print("xxxxxxxx")
	return render_template('admin/upload.html')