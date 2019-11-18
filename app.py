"""Main app file for the dashboard."""
import os

from flask import Flask, render_template
from flask_socketio import SocketIO
from apscheduler.schedulers.background import BackgroundScheduler

from _calendar import (write_housecalls,
                       read_housecalls,
                       read_water_status,
                       write_water_status)
from _itr import read_priority_tickets, write_priority_tickets
from _trello import read_unassigned_tasks, write_unassigned_tasks
from _redis import open_redis_connection

app = Flask(__name__)  # Flask instance
socketio = SocketIO(app)  # Using Flask SocketIO


def calendar():
    """Emit Google Calendar data."""
    print('[Google Calendar]: Running...')
    write_housecalls()
    housecalls = int(read_housecalls())
    write_water_status()
    status = bool(read_water_status())
    status_string = 'not' if not status else ''
    print('[Google Calendar]: {} housecalls'.format(housecalls))
    print('[Google Calendar]: It is {} water day'.format(status_string))
    socketio.emit('calendar', housecalls, broadcast=True)
    socketio.emit('water', status, broadcast=True)


def itr():
    """Emit ITR ticket data."""
    redis = open_redis_connection()
    num_tickets = redis.get('num_tickets')
    if not num_tickets:
        num_tickets = 0
    else:
        num_tickets = num_tickets.decode('utf-8')
    print('[ITR]: Running... ')
    write_priority_tickets()
    data_itr = read_priority_tickets()
    print('[ITR]: {} tickets'.format(len(data_itr['tickets'])))
    if int(num_tickets) < len(data_itr['tickets']):
        os.system('mpg123 sounds/new_ticket.mp3 &')
    elif int(num_tickets) > len(data_itr['tickets']):
        os.system('mpg123 sounds/done_ticket.mp3 &')
    redis.set('num_tickets', len(data_itr['tickets']), ex=30)
    socketio.emit('itr', data_itr, broadcast=True, json=True)


def trello():
    """Emit Trello data."""
    print('[Trello]: Running... ')
    write_unassigned_tasks()
    tasks = read_unassigned_tasks()
    print('[Trello]: {} technician tasks'.format(len(tasks)))
    socketio.emit('trello', tasks, broadcast=True, json=True)


"""Job Scheduling"""
scheduler = BackgroundScheduler()
# configure each job (how often it runs)
scheduler.add_job(calendar, 'interval', seconds=5, max_instances=1)
scheduler.add_job(itr, 'interval', seconds=10, max_instances=1)
scheduler.add_job(trello, 'interval', seconds=5, max_instances=1)


@app.route('/')
@app.route('/dashboard')
def dashboard():
    """Render Dashboard redirect function."""
    scheduler.start()
    return render_template('dashboard.html')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
