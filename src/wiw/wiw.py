import requests
from datetime import datetime, timedelta, timezone
from auth.auth import token
import pickle
import json

locations = '1593586, 3603580'
rcc_loc = '1593586'
stevenson_loc = '3603580'
root = 'https://api.wheniwork.com/'

today_params = {
                'location_id': locations,
                'start': datetime.today().strftime('%Y-%m-%d 00:00:00'),
                'end': datetime.today().strftime('%Y-%m-%d 23:59:59')
                }

""" User object, stores first/last name, user_id, and avatar_url """
class User:
    def __init__(self, first, last, user_id, avatar_url):
        self.first = first
        self.last = last
        self.user_id = user_id
        self.avatar =  avatar_url

    def __repr__(self):
        return '{} {} [{}]'.format(self.first, self.last, self.user_id)

""" Shift object, stores start/end time and user_id """
class Shift:
    def __init__(self, start, end, user_id):
        self.start = start
        self.end = end
        self.user_id = user_id
        self.start_dt = datetime.strptime(start, '%a, %d %b %Y %H:%M:%S %z')
        self.end_dt = datetime.strptime(end, '%a, %d %b %Y %H:%M:%S %z')

    def __repr__(self):
        return '{} {} [{}]'.format(self.start, self.end, self.user_id)

""" checks if a time is within a range """
def time_in_range(start, end, x):
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

""" get When I Work API response of shifts/users for the current day """
def wiw_shift_json():
    # set url to shifts target
    shift_root = root + '2/shifts'
    # return json of the shift information for the day
    return requests.get(shift_root, params=today_params, headers={"W-Token": token}).json()

""" get When I Work API response of clock ins for the current day """
def wiw_time_json(users):
    # set url to times target
    time_root = root + '2/times'
    # return json of time information for the day
    return requests.get(time_root, params=today_params, headers={"W-Token": token}).json()

""" get User objects from raw json """
def get_users(in_json):
    users_json = in_json['users']
    # return array of User objects made from json
    return [User(user['first_name'], user['last_name'], user['id'], user['avatar']) for user in users_json]

""" get Shift objects from raw json """
def get_shifts(in_json):
    shifts_json = in_json['shifts']
    # return array of Shift objects made from json
    return [Shift(shift['start_time'], shift['end_time'], shift['user_id']) for shift in shifts_json]

""" checks who is currently on shift """
def on_shift(shifts, users):
    # array of shifts that are active at the current time
    shifts_now = [shift for shift in shifts if time_in_range(shift.start_dt, shift.end_dt, datetime.now(timezone.utc))]
    for shift in shifts_now:
        # get user from shift object by id
        on_shift = next((x for x in users if shift.user_id == x.user_id), None)
        if on_shift is not None:
            print ('{} {}'.format(shift, on_shift))

""" pickle the given json """
def pickle_wiw(json):
    with open('wiw.pickle', 'wb') as pkl:
        pickle.dump(json, pkl)

""" open pickle given a filename """
def open_pickle(filename):
    data = None
    with open('wiw.pickle', 'rb') as pkl:
        data = pickle.load(pkl)
    return data

# wiw = wiw_shift_json()
# users = get_users(wiw)
# shifts = get_shifts(wiw)
#
# on_shift(shifts, users)
#
# pickle_wiw(wiw_shift_json())
