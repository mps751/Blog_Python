from flask import Flask, render_template, redirect, url_for, request, flash, Response
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, current_user, logout_user, login_user, login_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc, exc
import os.path
import os
 
app = Flask("app")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'chavesecreta'

UPLOAD_FOLDER = '/workspace/Blog_Python/static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
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

db.create_all()

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


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
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        try:
            new_user = User(username = username, email = email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
        except exc.IntegrityError:
            flash("Username or Email already exists")
            db.session.rollback()
        else:
            return redirect(url_for('login'))    
    return render_template('register.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash("Incorrect Username or Password")
            return redirect(url_for('login'))
        login_user(user)
        name = current_user.username
        if os.path.isfile('/workspace/Blog_Python/static/uploads/' + name + '.jpg'):
            return redirect(url_for('index'))
        else:
            return redirect(url_for('upload'))

    return render_template("login.html")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile/<string:username>', methods=['GET'])
@login_required
def profile(username):
    user = username
    posts = Post.query.order_by(desc(Post.created))
    return render_template('profile.html', posts = posts, user=user)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    try:
        p = Post.query.filter(Post.id == id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    return redirect(request.referrer)

@app.route('/delete_user/<int:id>')
@login_required
def delete_user(id):
    delete_img = str(current_user.username)+str('.jpg')
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], delete_img))
    user_id = User.query.filter(User.id==id).delete()
    db.session.commit()
    return redirect(url_for('index'))

def allowed_file(filename):
    return '.' in filename and \
           filename.split('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            Response ('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = str(current_user.username)+str('.jpg')
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('index'))
    return render_template("upload.html", name = current_user.username)