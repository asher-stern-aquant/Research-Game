import pickle

d = {'data1': [1, 2, 3],
     'data2': [4, 5, 6]}

with open('../models/pavel_model.pickle', 'wb') as f:
    pickle.dump(d, f)

