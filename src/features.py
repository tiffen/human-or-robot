import os.path
import functools

import numpy as np
import pandas as pd
from sklearn.base import TransformerMixin

from frequency import *
from utils import *

def feature_fullname(name, prefix=None):
    if not prefix:
        return name
    if not isinstance(prefix, basestring):
        prefix = '__'.join(tuple(prefix))
    return prefix + '__' + name

def feature_file(fullname):
    path = os.path.join('features', fullname.replace('__', os.sep) + '.csv')
    return workspace_file(path)

def save_features(names=(), prefix=''):
    if isinstance(names, basestring):
        names = (names,)
    def wrapper_outer(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for name in names:
                path = feature_file(feature_fullname(name, prefix))
                try_makedirs(os.path.dirname(path))
                features = func(name, *args, **kwargs)
                features.to_csv(path, index=True, header=True)
        return wrapper
    return wrapper_outer

class BidderFeature(TransformerMixin):
    def __init__(self, attribute):
        self.attribute = attribute

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        tokens = X[self.attribute].apply(lambda s: tuple(ord(x) for x in s))
        return tokens.apply(pd.Series).values

    def get_params(self, deep=True):
        return {'attribute': self.attribute}

class PrecomputedFeature(TransformerMixin):
    def __init__(self, name, default=None):
        self.name = name
        self.default = default
        self._load_features()

    def _load_features(self):
        path = feature_file(self.name)
        self.features = pd.read_csv(path, index_col='bidder_id')

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        features = self.features.reindex(X.index).values
        if self.default is not None:
            features[np.isnan(features)] = self.default
        return features

    def get_params(self, deep=True):
        return {'name': self.name, 'default': self.default}

@save_features(('merchandise', 'device', 'country', 'ip', 'url'), 'per_auction_freq')
def save_per_auction_freq(name, size=100):
    return bidder_per_auction_freq(name, auction_count=size)

if __name__ == '__main__':
    save_per_auction_freq()
