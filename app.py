from flask import Flask, render_template, request, jsonify
import requests
import random
import pickle

from wiw import wiw_get_users, wiw_get_shifts, wiw_on_shift, wiw_generate_new_pickle
from sheets import sheet_auth_login, sheet_get_values, sheet_auth_pickle
from utils import open_pickle, pickle_file

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/_loop')
def loop():
    out_json = {'wiw-rcc': [], 'wiw-stevenson': [], 'sheets': []}
    # When I Work
    wiw_generate_new_pickle()
    data_wiw = open_pickle('wiw.pickle')
    users = wiw_get_users(data_wiw)
    shifts = wiw_get_shifts(data_wiw)
    working = wiw_on_shift(shifts, users)
    out_json['wiw-rcc'] = [{'name': (user.first).split()[0], 'avatar': user.avatar} for user in working['rcc']]
    out_json['wiw-stevenson'] = [{'name': (user.first).split()[0], 'avatar': user.avatar} for user in working['stevenson']]
    # Google Sheets API
    data_sheets = open_pickle('sheets.pickle')
    sheet_auth_pickle()
    # make sure each row is the same length
    for row in data_sheets:
        while len(row) < 9:
            row.append('')

    out_json['sheets'] = [{
                            'task': row[0],
                            # 'description': row[1],
                            # 'techs': row[2],
                            # 'status': row[3],
                            # 'created': row[4],
                            # 'finished': row[5],
                            # 'due': row[6],
                            # 'notes': row[7],
                            # 'extra': row[8]
                            } for row in data_sheets[1:]]

    # print(out_json)

    return jsonify(out_json)

if __name__ == '__main__':
    app.run(debug=True)
