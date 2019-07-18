import pickle, json

""" pickle the given json """
def pickle_file(json, filename):
    with open('pickles/' + filename, 'wb') as pkl:
        pickle.dump(json, pkl)

""" open pickle given a filename (automatically prepends to the path to reference pickles folder) """
def open_pickle(filename):
    data = None
    with open('pickles/' + filename, 'rb') as pkl:
        data = pickle.load(pkl)
    return data

""" takes in dict and dump's it to a json file """
def json_file(data, filename):
    with open('json/' + filename, 'w') as json_out:
        json.dump(data, json_out, indent=4)

""" opens a json file and returs the associated dict """
def open_json(filename):
    data = None
    with open('json/' + filename, 'rb') as json_in:
        data = json.load(json_in)
    return data
