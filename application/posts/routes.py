from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from application import db
from application.models import Post, Comment, CommentLike, PostLike, TrustworthySubmission
from application.posts.forms import PostForm, ResponseForm
from .konspiratori_sk import konspiratory
from urllib.parse import urlparse

posts = Blueprint('posts', __name__)


@posts.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, url=form.url.data,
                    content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Váša otázka bola vytvorená a zverejnená', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='Opýtať sa otázku', form=form, legend='Opýtajte sa otázku')


def get_percent_of(true_or_false, post_id):
    all = TrustworthySubmission.query.filter_by(post_id=post_id).count()
    if all == 0:
        return 0
    count = TrustworthySubmission.query.filter_by(post_id=post_id)\
        .filter_by(is_trustworthy=true_or_false).count()
    return count / all * 100


def _calc_user_score(user):
    numerator = 0
    denominator = 0
    for comment in user.comments:
        q = CommentLike.query.filter_by(comment_id=comment.id)
        positive_interaction = q.filter_by(is_upvote=True).count()
        total_interaction = q.count()
        numerator += positive_interaction
        denominator += total_interaction
    return 0 if denominator == 0 else numerator/denominator


@posts.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    post.set_votable()
    comments = post.comments
    authors = []
    for comment in comments:
        comment.set_votable()
        authors.append(comment.author)
    for author in authors:
        author.score = _calc_user_score(author)
    true_percent = int(round(get_percent_of(True, post_id)))
    false_percent = int(round(get_percent_of(False, post_id)))
    domain = '.'.join(urlparse(post.url).netloc.split('.')[1:])
    is_in_konspiratory = domain in konspiratory
    form = ResponseForm()
    return render_template('post.html', post=post, form=form, comments=comments,
                           true_percent=true_percent, false_percent=false_percent,
                           is_in_konspiratory=is_in_konspiratory)


@posts.route('/post/<int:post_id>/true', methods=['POST'])
@login_required
def true_post(post_id):
    print('true_post')
    TrustworthySubmission.query.filter_by(user_id=current_user.id)\
        .filter_by(post_id=post_id)\
        .filter_by(is_trustworthy=False)\
        .delete()
    post = Post.query.get_or_404(post_id)
    ts = TrustworthySubmission(user=current_user, post=post, is_trustworthy=True)
    db.session.add(ts)
    db.session.commit()
    print(ts)
    return redirect(url_for('posts.post', post_id=post_id))


@posts.route('/post/<int:post_id>/false', methods=['POST'])
@login_required
def false_post(post_id):
    print('false_post')
    TrustworthySubmission.query.filter_by(user_id=current_user.id)\
        .filter_by(post_id=post_id)\
        .filter_by(is_trustworthy=True)\
        .delete()
    post = Post.query.get_or_404(post_id)
    ts = TrustworthySubmission(user=current_user, post=post, is_trustworthy=False)
    db.session.add(ts)
    db.session.commit()
    print(ts)
    return redirect(url_for('posts.post', post_id=post_id))


@posts.route('/post/<int:post_id>/comments/<int:comment_id>/upvote', methods=['POST'])
@login_required
def upvote_comment(post_id, comment_id):
    post = Post.query.get_or_404(post_id)
    comment = Comment.query.get_or_404(comment_id)
    like = CommentLike(user=current_user, comment=comment, is_upvote=True)
    db.session.add(like)
    db.session.commit()
    return redirect(url_for('posts.post', post_id=post.id))


@posts.route('/post/<int:post_id>/comments/<int:comment_id>/downvote', methods=['POST'])
@login_required
def downvote_comment(post_id, comment_id):
    post = Post.query.get_or_404(post_id)
    comment = Comment.query.get_or_404(comment_id)
    like = CommentLike(user=current_user, comment=comment, is_upvote=False)
    db.session.add(like)
    db.session.commit()
    return redirect(url_for('posts.post', post_id=post.id))


@posts.route('/post/<int:post_id>/upvote', methods=['POST'])
@login_required
def upvote_post(post_id):
    post = Post.query.get_or_404(post_id)
    like = PostLike(user=current_user, post=post, is_upvote=True)
    db.session.add(like)
    db.session.commit()
    return redirect(url_for('posts.post', post_id=post.id))


@posts.route('/post/<int:post_id>/downvote', methods=['POST'])
@login_required
def downvote_post(post_id):
    post = Post.query.get_or_404(post_id)
    like = PostLike(user=current_user, post=post, is_upvote=False)
    db.session.add(like)
    db.session.commit()
    return redirect(url_for('posts.post', post_id=post.id))


@posts.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Váša otázka bola úspešne upravená', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Upraviť otázku', form=form, legend='Upravte svoju otázku')


@posts.route('/post/<int:post_id>/comments', methods=['POST'])
@login_required
def add_post_comment(post_id):
    post = Post.query.get_or_404(post_id)
    form = ResponseForm()
    if form.validate_on_submit():
        comment = Comment(content=form.message.data, author=current_user, post=post)
        db.session.add(comment)
        db.session.commit()
        flash('Odpoveď bola pridaná', 'success')
    return redirect(url_for('posts.post', post_id=post_id))


@posts.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Vaša otázka bola vymazaná', 'success')
    return redirect(url_for('main.home'))


@posts.route('/delete/all', methods=['GET'])
def delete_db():
    db.drop_all()
    db.create_all()
    return('Hello World')
