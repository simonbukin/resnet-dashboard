from flask import Flask, render_template, request
from pusher import Pusher

app = Flask(__name__)

# need to define a Pusher object

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
