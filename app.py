from flask import Flask, render_template, redirect, url_for, request, flash, Response
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, current_user, logout_user, login_user, login_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
 
app = Flask("blog")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'chavesecreta'

UPLOAD_FOLDER = './upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
login = LoginManager(app)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    body = db.Column(db.String(500), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True, index=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    password_hash = db.Column(db.String(40), nullable=False)
    posts = db.relationship('Post', backref='author')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Img(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    img = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

db.create_all()

@app.route("/")
@app.route("/home", methods=["POST", "GET"])
def index():
    posts = Post.query.order_by(desc(Post.created)).all()
    if request.method == "POST":
        body = request.form['body']
        try:
            post = Post(body=body, author=current_user)
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('index'))
        except IntegrityError:
            flash("Error on create Post, try again later")
    return render_template('home.html', posts = posts)

@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        try:
            new_user = User(username = username, email = email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            flash("Username or Email already exists")
        else:
            return redirect(url_for('login'))    
    return render_template('register.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash("Incorrect Username or Password")
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('index'))

    return render_template("login.html")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile/<string:username>')
@login_required
def profile(username):
    posts = Post.query.order_by(desc(Post.created)).all()
    return render_template('profile.html', posts = posts)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    try:
        p = Post.query.filter(Post.id == id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    return redirect(request.referrer)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        pic = request.files['pic']

        filename = secure_filename(pic.filename)
        mimetype = pic.mimetype

        img = Img(img=pic.read(), mimetype=mimetype, name=filename)
        db.session.add(img)
        db.session.commit()

    return render_template("upload.html")

@app.route('/<int:id>')
def get_img(id):
    img = Img.query.filter_by(id=id).first()
    if not img:
        return 'Img Not Found!', 404

    return Response(img.img, mimetype=img.mimetype)