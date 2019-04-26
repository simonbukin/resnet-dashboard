from flask import Flask, render_template, request, jsonify
import requests
import random
import pickle

from src.wiw.wiw import get_users, get_shifts, on_shift, generate_new_pickle
from src.sheets.sheets import auth_login, get_sheet_values

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/')
@app.route('/dashboard')
def dashboard():
    generate_new_pickle()
    return render_template('dashboard.html')

@app.route('/_loop')
def loop():
    out_json = {'wiw': [], 'sheets': []}
    # wiw
    data_wiw = None
    with open('wiw.pickle', 'rb') as pkl:
        data_wiw = pickle.load(pkl)
    users = get_users(data_wiw)
    shifts = get_shifts(data_wiw)
    working = on_shift(shifts, users)
    out_json['wiw'] = [{'name': user.first} for user in working]
    # sheets
    data_sheets = None
    with open('src/sheets/data.pickle', 'rb') as pkl:
        data_sheets = pickle.load(pkl)

    for row in data_sheets:
        while len(row) < 9:
            row.append('')

    out_json['sheets'] = [{
                            'task': row[0],
                            'description': row[1],
                            'techs': row[2],
                            'status': row[3],
                            'created': row[4],
                            'finished': row[5],
                            'due': row[6],
                            'notes': row[7],
                            'extra': row[8]
                            } for row in data_sheets[1:]]

    # print(out_json)

    return jsonify(out_json)

if __name__ == '__main__':
    app.run(debug=True)
