import requests
from datetime import datetime, timedelta, timezone
from auth.auth import token
import pickle
import json
from utils import pickle_file, open_pickle

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
        # self.loc = loc

    def __repr__(self):
        return '{} {} [{}]'.format(self.first, self.last, self.user_id)

""" Shift object, stores start/end time and user_id. start and end _dt are just datetime objects of the start and end times """
class Shift:
    def __init__(self, start, end, user_id, loc):
        self.start = start
        self.end = end
        self.user_id = user_id
        self.start_dt = datetime.strptime(start, '%a, %d %b %Y %H:%M:%S %z')
        self.end_dt = datetime.strptime(end, '%a, %d %b %Y %H:%M:%S %z')
        if str(loc) == rcc_loc:
            self.loc = 'rcc'
        else:
            self.loc = 'stevenson'

    def __repr__(self):
        return '{} -> {} {} [{}]'.format(self.loc, self.start, self.end, self.user_id)

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

""" get When I Work API response of shifts for the current day """
def wiw_time_json(users):
    # set url to times target
    time_root = root + '2/times'
    # return json of time information for the day
    return requests.get(time_root, params=today_params, headers={"W-Token": token}).json()

""" get clockins from WIW """
def wiw_clockin_json():
    wiw = wiw_shift_json()
    users = wiw_get_users(wiw)
    clockin_root = root + '2/times/user/'
    for user in users:
        print(clockin_root + str(user.user_id))
        req = requests.get(clockin_root + str(user.user_id), headers={"W-Token": token})
        print(req)

""" convert raw json to array of User objects """
def wiw_get_users(in_json):
    users_json = in_json['users']
    return [User(user['first_name'], user['last_name'], user['id'], user['avatar']['url'][:-3]) for user in users_json]

""" convert raw json to array of Shift objects """
def wiw_get_shifts(in_json):
    shifts_json = in_json['shifts']
    # print(shifts_json)
    # return array of Shift objects made from json
    return [Shift(shift['start_time'], shift['end_time'], shift['user_id'], shift['location_id']) for shift in shifts_json]

""" returns list of Users on that are on a Shift """
def wiw_on_shift(shifts, users):
    # array of shifts that are active at the current time
    shifts_now = [shift for shift in shifts if time_in_range(shift.start_dt, shift.end_dt, datetime.now(timezone.utc))]
    users_on_shift = {'rcc': [], 'stevenson': []}
    # return shifts_now
    for shift in shifts_now:
        # get user from shift object by id
        on_shift = next((x for x in users if shift.user_id == x.user_id), None)
        if on_shift is not None:
            if shift.loc == 'rcc':
                users_on_shift['rcc'].append(on_shift)
            else:
                users_on_shift['stevenson'].append(on_shift)
    return users_on_shift

""" update the wiw.pickle file with new json """
def wiw_generate_new_pickle():
    wiw = wiw_shift_json()
    users = wiw_get_users(wiw)
    shifts = wiw_get_shifts(wiw)
    pickle_file(wiw_shift_json(), 'wiw.pickle')
