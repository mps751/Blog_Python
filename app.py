from flask import Flask, render_template, redirect
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
 
app = Flask("hello")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(70), nullable=False)
    body = db.Column(db.String(500), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True, index=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    password_hash = db.Column(db.String(40), nullable=False)
    posts = db.relationship('Post', backref='author')

db.create_all()

@app.route("/")
@app.route('/home')
def index():
    posts = Post.query.all()
    return render_template('home.html', posts = posts)

@app.route("/mok")
def mok():
    user = User(username='matheus', email='matheus.silva', password_hash='aaa')
    post1 = Post(title='post 1', body='texto do post 1', author=user)
    db.session.add(post1)
    db.session.commit()
    return redirect("/")