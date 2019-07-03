from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from apscheduler.schedulers.background import BackgroundScheduler
import requests, random, pickle

from _wiw import wiw_get_users, wiw_get_shifts, wiw_on_shift, wiw_generate_new_pickle
from _sheets import sheet_auth_login, sheet_get_values, sheet_auth_pickle
from _utils import open_pickle, pickle_file
from _calendar import calendar_auth_login, calendar_get_events, calendar_auth_pickle, housecall_status

app = Flask(__name__)
socketio = SocketIO(app)

def wiw():
    print("wiw job running")
    wiw_generate_new_pickle()
    data_wiw = open_pickle('wiw.pickle')
    users = wiw_get_users(data_wiw)
    shifts = wiw_get_shifts(data_wiw)
    working = wiw_on_shift(shifts, users)
    rcc = [{'name': (user.first).split()[0], 'avatar': user.avatar, 'loc': 'rcc'} for user in working['rcc']]
    stevenson = [{'name': (user.first).split()[0], 'avatar': user.avatar, 'loc': 'stevenson'} for user in working['stevenson']]
    print(rcc+stevenson)
    socketio.emit('wiw', rcc + stevenson, broadcast=True, json=True)

def sheets():
    print("sheets job running")
    sheet_auth_pickle()
    data_sheets = open_pickle('sheets.pickle')
    for row in data_sheets: # set row length correctly
        while len(row) < 9:
            row.append('')
    data_sheets = [{'task': row[0]} for row in data_sheets[1:]]
    # print(data_sheets)
    socketio.emit('sheets', data_sheets, broadcast=True, json=True)

def calendar():
    print("calendar job running")
    calendar_auth_pickle()
    data_calendar = open_pickle('calendar.pickle')
    print('housecalls: {}'.format(housecall_status(data_calendar)))
    socketio.emit('calendar', housecall_status(data_calendar), broadcast=True)

#schedule job
scheduler = BackgroundScheduler()
scheduler.add_job(wiw, 'interval', seconds=3, max_instances=1)
scheduler.add_job(sheets, 'interval', seconds=3, max_instances=1)
scheduler.add_job(calendar, 'interval', seconds=3, max_instances=1)

@app.route('/')
@app.route('/dashboard')
def dashboard():
    scheduler.start()
    return render_template('dashboard.html')

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0")
