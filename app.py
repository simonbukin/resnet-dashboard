from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import random
import webbrowser
import os

from _wiw import wiw_get_users, wiw_get_shifts, wiw_on_shift, wiw_generate_new_json
from _sheets import sheet_auth_login, sheet_get_values, sheet_auth_json
from _utils import open_json, json_file
from _calendar import calendar_auth_login, calendar_get_events, calendar_auth_json, housecall_status
from _itr import itr_json, high_priority
from _trello import trello_json

app = Flask(__name__)  # Flask instance
socketio = SocketIO(app)  # Using Flask SocketIO

fake_data = False  # flag for using fake ITR data fo testing


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


def sheets():
    """Emit Technician Task data."""
    print('[Google Sheets]: Running...')
    sheet_auth_json()  # authenticate and refresh sheets.json
    data_sheets = open_json('sheets.json')  # open new data
    socketio.emit('sheets', data_sheets, broadcast=True, json=True)


def calendar():
    """Emit Google Calendar Housecall data."""
    print('[Google Calendar]: Running...')
    calendar_auth_json()  # authenticate and refresh calendar.json
    data_calendar = open_json('calendar.json')  # open new data
    housecalls = housecall_status(data_calendar['events'])
    print('[Google Calendar]: {} housecalls'.format(housecalls))
    socketio.emit('calendar', housecalls, broadcast=True)


num_tickets = 0


def itr():
    """Emit ITR ticket data."""
    global num_tickets
    print('[ITR]: Running... ')
    itr_json()  # refresh itr.json
    data_itr = open_json('itr.json')  # open new data
    print('[ITR]: {} tickets'.format(len(data_itr['tickets'])))
    if num_tickets < len(data_itr['tickets']):
        os.system('mpg123 new.mp3')
    elif num_tickets > len(data_itr['tickets']):
        os.system('mpg123 done.mp3')
    num_tickets = len(data_itr['tickets'])
    socketio.emit('itr', data_itr, broadcast=True, json=True)

def trello():
    """Emit Trello data."""
    print('[Trello]: Running... ')
    trello_json()
    data_trello = open_json('trello.json')
    print('[Trello]: {} technician tasks'.format(len(data_trello)))
    socketio.emit('trello', data_trello, broadcast=True, json=True)

def fake_itr():
    """Emit fake ITR data for testing."""
    print('[Fake ITR]: Running...')
    fake_itr_data = open_json('fake_itr.json')  # open fake data
    socketio.emit('itr', fake_itr_data, broadcast=True, json=True)


""" Job Scheduling """
scheduler = BackgroundScheduler()  # create a scheduler
if(fake_data):  # using fake data only
    scheduler.add_job(fake_itr, 'interval', seconds=3, max_instances=1)
else:  # only real data
    # configure each job (how often it runs)
    scheduler.add_job(wiw, 'interval', seconds=60, max_instances=1)
    # scheduler.add_job(sheets, 'interval', seconds=5, max_instances=1)
    scheduler.add_job(calendar, 'interval', seconds=5, max_instances=1)
    scheduler.add_job(itr, 'interval', seconds=10, max_instances=1)
    scheduler.add_job(trello, 'interval', seconds=5, max_instances=1)


@app.route('/')  # main redirect
@app.route('/dashboard')
def dashboard():
    """Render Dashboard redirect function."""
    scheduler.start()  # start scheduler
    return render_template('dashboard.html')  # render dashboard


def open_browser():
    """Open browser."""
    webbrowser.open_new('http://0.0.0.0:5000/')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
