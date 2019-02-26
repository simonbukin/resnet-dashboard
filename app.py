from flask import Flask, render_template, request, jsonify
import requests
import random

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/_loop')
def loop():
    test_json = 'https://jsonplaceholder.typicode.com/users'
    r = requests.get(test_json)
    rand_users = random.sample(r.json(), random.choice(range(1,10)))
    return jsonify(rand_users)

if __name__ == '__main__':
    app.run(debug=True)
