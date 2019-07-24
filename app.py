from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from apscheduler.schedulers.background import BackgroundScheduler
import requests, random

from _wiw import wiw_get_users, wiw_get_shifts, wiw_on_shift, wiw_generate_new_json
from _sheets import sheet_auth_login, sheet_get_values, sheet_auth_json
from _utils import open_json, json_file
from _calendar import calendar_auth_login, calendar_get_events, calendar_auth_json, housecall_status
from _itr import itr_json, high_priority

import webbrowser
from threading import Timer

app = Flask(__name__)
socketio = SocketIO(app)

fake_data = False

def wiw():
    print("wiw job running")
    wiw_generate_new_json()
    data_wiw = open_json('wiw.json')
    users = wiw_get_users(data_wiw)
    shifts = wiw_get_shifts(data_wiw)
    working = wiw_on_shift(shifts, users)
    rcc = [{'name': (user.first).split()[0], 'avatar': user.avatar, 'loc': 'rcc'} for user in working['rcc']]
    stevenson = [{'name': (user.first).split()[0], 'avatar': user.avatar, 'loc': 'stevenson'} for user in working['stevenson']]
    print(rcc + stevenson)
    socketio.emit('wiw', rcc + stevenson, broadcast=True, json=True)

def sheets():
    print("sheets job running")
    sheet_auth_json()
    data_sheets = open_json('sheets.json')
    socketio.emit('sheets', data_sheets, broadcast=True, json=True)

def calendar():
    print("calendar job running")
    calendar_auth_json()
    data_calendar = open_json('calendar.json')
    socketio.emit('calendar', housecall_status(data_calendar['events']), broadcast=True)

def itr():
    print('itr job running')
    itr_json()
    data_itr = open_json('itr.json')
    socketio.emit('itr', data_itr, broadcast=True, json=True)

def fake_itr():
    print('fake itr job running')
    fake_itr_data = open_json('fake_itr.json')
    socketio.emit('itr', fake_itr_data, broadcast=True, json=True)

#schedule job
scheduler = BackgroundScheduler()
if(fake_data):
    scheduler.add_job(fake_itr, 'interval', seconds=3, max_instances=2)
else:
    scheduler.add_job(wiw, 'interval', seconds=60, max_instances=2)
    scheduler.add_job(sheets, 'interval', seconds=5, max_instances=2)
    scheduler.add_job(calendar, 'interval', seconds=5, max_instances=2)
    scheduler.add_job(itr, 'interval', seconds=10, max_instances=2)

@app.route('/')
@app.route('/dashboard')
def dashboard():
    scheduler.start()
    return render_template('dashboard.html')

def open_browser():
    webbrowser.open_new('http://0.0.0.0:5000/')

if __name__ == '__main__':
#     # Timer(1, open_browser).start()
    socketio.run(app, host="0.0.0.0")
