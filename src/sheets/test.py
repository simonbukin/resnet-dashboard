import pickle

with open('data.pickle', 'rb') as pkl:
    data = pickle.load(pkl)

for row in data:
    print(row)
