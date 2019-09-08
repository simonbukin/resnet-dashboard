"""Main app file for the dashboard."""
import os

from flask import Flask, render_template
from flask_socketio import SocketIO
from apscheduler.schedulers.background import BackgroundScheduler

from _wiw import (wiw_get_users,
                  wiw_get_shifts,
                  wiw_on_shift,
                  wiw_generate_new_json)
from _utils import open_json
from _calendar import (write_housecalls,
                       read_housecalls)
from _itr import itr_json, read_priority_tickets, write_priority_tickets
from _trello import read_unassigned_tasks, write_unassigned_tasks

app = Flask(__name__)  # Flask instance
socketio = SocketIO(app)  # Using Flask SocketIO


def wiw():
    """Emit When I Work data."""
    print('[When I Work]: Running...')
    wiw_generate_new_json()  # update json
    data_wiw = open_json('wiw.json')  # open it
    users = wiw_get_users(data_wiw)  # get users
    shifts = wiw_get_shifts(data_wiw)  # get shifts
    working = wiw_on_shift(shifts, users)  # get who is currently working
    # split user by who is working where
    rcc = [{'name': (user.first).split()[0],
            'avatar': user.avatar,
            'loc': 'rcc'} for user in working['rcc']]
    stevenson = [{'name': (user.first).split()[0],
                  'avatar': user.avatar,
                  'loc': 'stevenson'} for user in working['stevenson']]
    print("[When I Work]: {} at RCC, {} at Stevenson".format(
                                                            len(rcc),
                                                            len(stevenson)))
    socketio.emit('wiw', rcc + stevenson, broadcast=True, json=True)


def calendar():
    """Emit Google Calendar Housecall data."""
    print('[Google Calendar]: Running...')
    write_housecalls()
    # calendar_auth_json()  # authenticate and refresh calendar.json
    # data_calendar = open_json('calendar.json')  # open new data
    # housecalls = housecall_status(data_calendar['events'])
    housecalls = int(read_housecalls())
    print('[Google Calendar]: {} housecalls'.format(housecalls))
    socketio.emit('calendar', housecalls, broadcast=True)


num_tickets = 0


def itr():
    """Emit ITR ticket data."""
    global num_tickets
    print('[ITR]: Running... ')
    write_priority_tickets()
    data_itr = read_priority_tickets()
    print('[ITR]: {} tickets'.format(len(data_itr['tickets'])))
    if num_tickets < len(data_itr['tickets']):
        os.system('mpg123 sounds/new_ticket.mp3')
    elif num_tickets > len(data_itr['tickets']):
        os.system('mpg123 sounds/done_ticket.mp3')
    num_tickets = len(data_itr['tickets'])
    socketio.emit('itr', data_itr, broadcast=True, json=True)


def trello():
    """Emit Trello data."""
    print('[Trello]: Running... ')
    write_unassigned_tasks()
    tasks = read_unassigned_tasks()
    print('[Trello]: {} technician tasks'.format(len(tasks)))
    socketio.emit('trello', tasks, broadcast=True, json=True)


""" Job Scheduling """
scheduler = BackgroundScheduler()  # create a scheduler
# configure each job (how often it runs)
scheduler.add_job(wiw, 'interval', seconds=60, max_instances=1)
scheduler.add_job(calendar, 'interval', seconds=5, max_instances=1)
scheduler.add_job(itr, 'interval', seconds=10, max_instances=1)
scheduler.add_job(trello, 'interval', seconds=5, max_instances=1)


@app.route('/')  # main redirect
@app.route('/dashboard')
def dashboard():
    """Render Dashboard redirect function."""
    scheduler.start()  # start scheduler
    return render_template('dashboard.html')  # render dashboard


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
