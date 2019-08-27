import json


def json_file(data, filename):
    """Takes in dict and dump's it to a json file."""
    with open('json/' + filename, 'w') as json_out:
        json.dump(data, json_out, indent=4)


def open_json(filename):
    """Opens a json file and returs the associated dict."""
    data = None
    with open('json/' + filename, 'rb') as json_in:
        data = json.load(json_in)
    return data


def time_in_range(start, end, x):
    """Checks if a time is within a range."""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end
