"""Create an entry point for gunicorn."""

from app import flask_app

if __name__ == '__main__':
    flask_app.run(debug=True)
