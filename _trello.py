import requests
from auth.auth import technician_board_id, trello_key, trello_token, unassigned_list_id
from _utils import json_file

api_url = 'https://api.trello.com'

# using /1/lists/{id}/cards?fields=name to get all cards from list


def get_unassigned_tasks():
    """Get cards from unassigned tasks board."""
    lists_endpoint = '/1/lists/{}/cards?'.format(unassigned_list_id)
    params = {
        'field': 'name',
        'key': trello_key,
        'token': trello_token
    }
    r = None
    try:
        r = requests.get(api_url + lists_endpoint, params=params)
        print(r.url)
    except Exception:
        print('error in requests call')
    return [card['name'] for card in r.json()]


def trello_json():
    """Write Trello data to JSON."""
    json_file(get_unassigned_tasks(), 'trello.json')


print(get_unassigned_tasks())
