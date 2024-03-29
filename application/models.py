from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from application import db, login_manager
from flask_login import UserMixin, current_user

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    comment_likes = db.relationship('CommentLike', backref='user', lazy=True)
    post_likes = db.relationship('PostLike', backref='user', lazy=True)
    trustworthy_submissions = db.relationship('TrustworthySubmission', backref='user', lazy=True)

    score = 0

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title =  db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(250), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    comments = db.relationship('Comment', backref='post', lazy=True)
    likes = db.relationship('PostLike', backref='post', lazy=True)
    trustworthy_submissions = db.relationship('TrustworthySubmission', backref='post', lazy=True)
    keywords = db.relationship('KeyWord', backref='post', lazy=True)

    votes = 0
    can_upvote = True
    can_downvote = True

    def set_votable(self):
        self.votes = 0
        for vote in self.likes:
            self.votes = self.votes + 1 if vote.is_upvote else self.votes - 1
        if current_user.is_authenticated:
            upvoted = PostLike.query.filter_by(post_id=self.id)\
                .filter_by(user_id=current_user.id).filter_by(is_upvote=True).count()
            downvoted = PostLike.query.filter_by(post_id=self.id)\
                .filter_by(user_id=current_user.id).filter_by(is_upvote=False).count()
            if upvoted-downvoted > 0:
                self.can_upvote = False
            if upvoted-downvoted < 0:
                self.can_downvote = False

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    likes = db.relationship('CommentLike', backref='comment', lazy=True)
    votes = 0
    can_upvote = True
    can_downvote = True

    def set_votable(self):
        self.votes = 0
        for vote in self.likes:
            self.votes = self.votes + 1 if vote.is_upvote else self.votes - 1
        if current_user.is_authenticated:
            upvoted = CommentLike.query.filter_by(comment_id=self.id)\
                .filter_by(user_id=current_user.id).filter_by(is_upvote=True).count()
            downvoted = CommentLike.query.filter_by(comment_id=self.id)\
                .filter_by(user_id=current_user.id).filter_by(is_upvote=False).count()
            if upvoted-downvoted > 0:
                self.can_upvote = False
            if upvoted-downvoted < 0:
                self.can_downvote = False


class CommentLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)
    is_upvote = db.Column(db.Boolean, nullable=False)


class PostLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    is_upvote = db.Column(db.Boolean, nullable=False)


class TrustworthySubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    is_trustworthy = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"TS('{self.id}', '{self.post_id}', '{self.is_trustworthy}')"


class KeyWord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    word = db.Column(db.String(40), unique=False, nullable=False)
