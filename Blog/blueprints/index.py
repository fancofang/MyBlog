from flask import flash, url_for, redirect, request, current_app, render_template, jsonify
from flask.blueprints import Blueprint
from Blog.models import Post, Message
from Blog.form import HelloForm
from Blog.extensions import db, csrf
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
index_bp = Blueprint('index',__name__)


@index_bp.route('/', methods=['GET'])
def index():
    last = Post.query.order_by(Post.timestamp.desc()).first()
    form = HelloForm()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MESSAGE_PER_PAGE']
    pagination = Message.query.order_by(Message.timestamp.desc()).paginate(page, per_page=per_page)
    messages = pagination.items

    return render_template('index.html', post=last, pagination=pagination, messages=messages, form=form)

@csrf.exempt
@index_bp.route('/index/message', methods=['POST'])
def message():
    data = request.get_json()
    if request.method == 'POST':
        name = data['name']
        body = data['body']
        message = Message(body=body, name=name)
        db.session.add(message)
        db.session.commit()
        # return jsonify({'result' : 'yes'})
        # flash('Your message have been sent to the world!')
        return render_template('_message.html', message=message)
    return jsonify({'result':'error'})
