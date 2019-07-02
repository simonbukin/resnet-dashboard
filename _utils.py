import pickle

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
