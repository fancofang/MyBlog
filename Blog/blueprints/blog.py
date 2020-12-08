from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for, session, jsonify
from flask_login import current_user
from Blog.models import Post, Category, Comment, User
from Blog.utils import redirect_back
from Blog.extensions import db
from Blog.form import CommentForm, CommentFormHiddenEmail
from Blog.emails import send_someone_connect_email

blog_bp = Blueprint('blog', __name__)

@blog_bp.route('/posts')
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

# @blog_bp.route('/post/<param>', methods=['GET', 'POST'])
# def show_post(param):
#     post = Post.query.filter_by(title=param).first_or_404()
#     page = request.args.get('page', 1, type=int)
#     per_page = current_app.config['BLOG_POST_PER_PAGE']
#     comment_pagination = Comment.query.filter_by(post_id=post.id).order_by(Comment.timestamp.desc()).paginate(
#         page, per_page)
#     comments = comment_pagination.items
#     form = CommentForm()
#     if form.validate_on_submit():
#         if current_user.is_authenticated:
#             body = form.body.data
#             author = current_user
#             comment = Comment(body=body, post=post, author= author)
#             replied_id = request.args.get('reply')
#             if replied_id:
#                 replied_comment = Comment.query.get_or_404(replied_id)
#                 comment.replied = replied_comment
#             db.session.add(comment)
#             db.session.commit()
#             return redirect(url_for('blog.show_post', param=param))
#         else:
#             flash('Please login first.', 'warning')
#             return redirect(url_for('auth.login'))
#     return render_template('blog/post.html', pagination=comment_pagination, post=post, comments=comments, form=form)

@blog_bp.route('/post/<param>', methods=['GET'])
def show_post(param):
    post = Post.query.filter_by(title=param).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLOG_POST_PER_PAGE']
    comment_pagination = Comment.query.filter_by(post_id=post.id).order_by(Comment.timestamp.desc()).paginate(
        page, per_page)
    comments = comment_pagination.items
    if current_user.is_authenticated or 'browser_email' in session:
        form = CommentFormHiddenEmail()
        form.email.data = current_user.email if not current_user.is_anonymous else session['browser_email']
    else:
        form = CommentForm()
    try:
        form.name.data = current_user.username
    except:
        form.name.data = session['browser_user'] if ('browser_user' in session) else None
    return render_template('blog/post.html', pagination=comment_pagination, post=post, comments=comments, form=form)

@blog_bp.route('/post/<param>/comment', methods=['POST'])
def leave_comment(param):
    post = Post.query.filter_by(title=param).first_or_404()
    if request.method == 'POST':
        email = request.form.get('email',None)
        user = User.query.filter_by(email=email).first()
        if not user:
            author = request.form.get('name', None)
            user = User(username=author, email=email)
        else:
            author = user.username
        body = request.form.get('body', None)
        comment = Comment(body=body, post=post, author_id=user.id)
        db.session.add(comment)
        replied_id = request.form.get('be_reply',None)
        if replied_id:
            replied_comment = Comment.query.get_or_404(replied_id)
            comment.replied = replied_comment
        if request.form.get('remember',None):
            session['browser_email'] = email
            session['browser_user'] = author
        db.session.commit()
        return redirect(url_for('blog.show_post', param=post.title) + '#comments')
    # return render_template('blog/post.html', post=post, comments=comments, form=form)


@blog_bp.route('/reply')
def reply_comment():
    comment_id = request.args.get('comment_id')
    if comment_id:
        replied_comment = Comment.query.get_or_404(comment_id)
        return render_template('blog/_reply.html', comment=replied_comment)
    print(comment_id)
    return comment_id
    # comment = Comment.query.get_or_404(comment_id)
    # post = Post.query.get_or_404(comment.post_id)
    # print(comment.post_id)
    # if not comment.post.can_comment:
    #     flash('Comment is disabled.', 'warning')
    #     return redirect(url_for('blog.show_post', param=comment.post.title))
    # return redirect(
    #     url_for('blog.show_post', param=post.title, reply=comment_id) + '#comment-form')


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


@blog_bp.route('/test')
def test():
    return jsonify({"a":1})

    