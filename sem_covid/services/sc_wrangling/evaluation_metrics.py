import pandas as pd
from numpy.core.records import ndarray
from pandas import Series
from sklearn.metrics import (f1_score, precision_score, accuracy_score,
                             recall_score, mean_squared_error, mean_absolute_error, roc_auc_score)


def model_evaluation_metrics(actual_data: Series, predicted_data: ndarray):
    """
        assuming we have actual test and predicted labels
        and we want to see the evaluation score of those 2 labels
        :actual_data: the real test label
        :predicted_data: predicted label
        :return: the evaluation metrics result in dictionary form
    """
    accuracy = accuracy_score(actual_data, predicted_data)
    precision = precision_score(actual_data, predicted_data, average="macro")
    recall = recall_score(actual_data, predicted_data, average="macro")
    f1 = f1_score(actual_data, predicted_data, average="macro")
    mae = mean_absolute_error(actual_data, predicted_data)
    mse = mean_squared_error(actual_data, predicted_data)
    roc_auc = roc_auc_score(actual_data, predicted_data, multi_class='ovr')

    metric_lables = ['Accuracy', 'Precision', 'Recall',
                     'F1-Score', 'Mean Absolute Error',
                     'Mean Squared Error', 'ROC AUC Score']

    metric_values = [accuracy, precision, recall, f1, mae, mse, roc_auc]

    return {key: values for key, values in zip(metric_lables, metric_values)}
