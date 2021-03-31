
from sklearn.preprocessing import LabelEncoder


class MultiColumnLabelEncoder:
    """Encode multiple columns for a DataFrame"""
    def __init__(self, columns: list = None):
        self.columns = columns

    def fit(self, x, y=None):
        return self

    def transform(self, x):

        # Transforms columns of X specified in self.columns using
        # LabelEncoder(). If no columns specified, transforms all
        # columns in X.

        output = x.copy()
        if self.columns is not None:
            for col in self.columns:
                output[col] = LabelEncoder().fit_transform(output[col])
        else:
            for colname, col in output.iteritems():
                output[colname] = LabelEncoder().fit_transform(col)
        return output

    def fit_transform(self, x, y=None):
        return self.fit(x, y).transform(x)
