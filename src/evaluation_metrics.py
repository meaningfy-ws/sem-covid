import pandas as pd
from numpy.core.records import ndarray
from pandas import Series
from sklearn.metrics import (f1_score, precision_score, accuracy_score,
                             recall_score, mean_squared_error, mean_absolute_error)


def evaluation(actual: Series, prediction: ndarray, title: str):
    """
    assuming we have actual test and predicted labels
    and we want to see the evaluation score of those 2 labels
    :actual: the real test label
    :prediction: predicted label
    :title: column title of the DataFrame
    """
    accuracy = accuracy_score(actual, prediction)
    precision = precision_score(actual, prediction, average="macro")
    recall = recall_score(actual, prediction, average="macro")
    f1 = f1_score(actual, prediction, average="macro")
    mae = mean_absolute_error(actual, prediction)
    mse = mean_squared_error(actual, prediction)

    evaluate_metrics = pd.DataFrame({'Evaluation Metrics': ['Accuracy', 'Precission', 'Recall',
                                                            'F1 Score', 'Mean Absolute Error',
                                                            'Mean Squared Error'],
                                     title: [accuracy, precision, recall, f1, mae, mse]})

    return evaluate_metrics
