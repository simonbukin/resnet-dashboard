"""Retrieve tasks from Trello."""
import requests

from auth.auth import trello_key, trello_token, unassigned_list_id
from _redis import open_redis_connection

api_url = 'https://api.trello.com'


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
    except Exception:
        print('error in requests call')
    return [card['name'] for card in r.json()]


def write_unassigned_tasks():
    """Write a list of unassigned tasks to Redis."""
    redis = open_redis_connection()
    redis.delete('tech_tasks')
    unassigned_tasks = get_unassigned_tasks()
    redis.lpush('tech_tasks', *unassigned_tasks)  # "map" results


def read_unassigned_tasks():
    """Read and decode technician tasks into a list."""
    redis = open_redis_connection()
    unassigned_tasks = redis.lrange('tech_tasks', 0, -1)
    format_tasks = [task.decode('UTF-8') for task in unassigned_tasks]
    return format_tasks
