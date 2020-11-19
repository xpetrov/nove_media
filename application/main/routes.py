from flask import render_template, request, Blueprint
from flask_login import current_user
from application.models import Post, PostLike

main = Blueprint('main', __name__)


authors = [
    'Dresto Filip',
    'Maliniaková Karin',
    'Nemeček Andrej',
    'Petrov Ivan'
]


@main.route('/')
@main.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    for post in posts.items:
        post.set_votable()
    return render_template('home.html', posts=posts)


@main.route('/about')
def about():
    return render_template('about.html', title='About', authors=authors)
