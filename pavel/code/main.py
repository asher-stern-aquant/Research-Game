import pickle

with open('../models/pavel_model.pickle', 'rb') as f:
    d = pickle.load(f)

d = {k: [2*i for i in v] for k, v in d.items()}

with open('../models/pavel_model.pickle', 'wb') as f:
    pickle.dump(d, f)

