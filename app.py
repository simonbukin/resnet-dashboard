from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from apscheduler.schedulers.background import BackgroundScheduler
import requests, random, pickle

from _wiw import wiw_get_users, wiw_get_shifts, wiw_on_shift, wiw_generate_new_pickle
from _sheets import sheet_auth_login, sheet_get_values, sheet_auth_pickle
from _utils import open_pickle, open_json, pickle_file, json_file
from _calendar import calendar_auth_login, calendar_get_events, calendar_auth_json, housecall_status
from _itr import itr_pickle, itr_json, high_priority

app = Flask(__name__)
socketio = SocketIO(app)

fake_data = False

def wiw():
    print("wiw job running")
    wiw_generate_new_pickle()
    data_wiw = open_pickle('wiw.pickle')
    users = wiw_get_users(data_wiw)
    shifts = wiw_get_shifts(data_wiw)
    working = wiw_on_shift(shifts, users)
    rcc = [{'name': (user.first).split()[0], 'avatar': user.avatar, 'loc': 'rcc'} for user in working['rcc']]
    # rcc += [{'name': 'doge' + str(random.randint(3,40))} for x in range(0,20)]
    stevenson = [{'name': (user.first).split()[0], 'avatar': user.avatar, 'loc': 'stevenson'} for user in working['stevenson']]
    # stevenson += [{'name': 'doge' + str(random.randint(3,40))} for x in range(0,20)]
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
    socketio.emit('sheets', data_sheets, broadcast=True, json=True)

def calendar():
    print("calendar job running")
    calendar_auth_json()
    data_calendar = open_json('calendar.json')
    socketio.emit('calendar', housecall_status(data_calendar['events']), broadcast=True)

def itr():
    print('itr job running')
    itr_pickle()
    data_itr = open_pickle('itr.pickle')
    socketio.emit('itr', data_itr, broadcast=True, json=True)

def fake_itr():
    print('fake itr job running')
    # itr_json()
    fake_itr_data = open_json('itr.json')
    # print(fake_itr_data)
    # fake_itr_data = open_pickle('itr.pickle')
    socketio.emit('itr', fake_itr_data, broadcast=True, json=True)

#schedule job
scheduler = BackgroundScheduler()
if(fake_data):
    scheduler.add_job(fake_itr, 'interval', seconds=3, max_instances=1)
else:
    scheduler.add_job(wiw, 'interval', seconds=60, max_instances=1)
    scheduler.add_job(sheets, 'interval', seconds=5, max_instances=1)
    scheduler.add_job(calendar, 'interval', seconds=5, max_instances=1)
    scheduler.add_job(itr, 'interval', seconds=10, max_instances=1)

@app.route('/')
@app.route('/dashboard')
def dashboard():
    scheduler.start()
    return render_template('dashboard.html')

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0")
