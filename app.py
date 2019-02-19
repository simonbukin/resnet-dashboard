from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

inc = 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/_loop')
def loop():
    global inc
    inc += 1
    return jsonify(result=inc)

if __name__ == '__main__':
    app.run(debug=True)
