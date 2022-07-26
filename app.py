from flask import Flask, render_template
 
app = Flask("'hello'")

@app.route("/")
def hello():
    return render_template('index.html') 