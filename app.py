from flask import Flask, render_template
from datetime import datetime
 
app = Flask("'hello'")

posts = [
    {
        'title': "primeiro post",
        'body': "texto do post",
        'author': "autor",
        'created': datetime(2022,7,25)
    }
]

@app.route("/")
@app.route('/home')
def index():
    return render_template('index.html', posts = posts) 