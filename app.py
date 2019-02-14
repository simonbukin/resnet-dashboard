from flask import Flask, render_template, request
from pusher import Pusher

app = Flask(__name__)

# should probably not be plaintext
pusher_client = Pusher(
  app_id='712785',
  key='3e300f51e329d8c1f95d',
  secret='282c04076bddc1c75bc7',
  cluster='us2',
  ssl=True
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    # pusher_client.trigger('tickets', 'new-ticket', {'message': "i'm at the root"})
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
