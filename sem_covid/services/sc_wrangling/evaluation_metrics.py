import pandas as pd
from numpy.core.records import ndarray

from sklearn.metrics import (f1_score, precision_score, accuracy_score,
                             recall_score, mean_squared_error, mean_absolute_error, roc_auc_score)


def model_evaluation_metrics(actual_data: pd.Series, predicted_data: ndarray) -> dict:
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

    metric_lables = ['Accuracy', 'Precision', 'Recall',
                     'F1-Score', 'Mean Absolute Error',
                     'Mean Squared Error', 'ROC AUC Score']

    metric_values = [accuracy, precision, recall, f1, mae, mse]

    return {key: values for key, values in zip(metric_lables, metric_values)}


def calculate_roc_auc_multiclass(actual_data: pd.Series, predicted_data: ndarray, average: str = 'macro') -> dict:
    """
        this function helps us to calculate ROC AUC Score for each classifier in inserted data
    """
    unique_data = set(actual_data)
    roc_auc_dictionary = {}

    for each_data in unique_data:
        other_data = [element for element in unique_data if element != each_data]
        new_data = [0 if element in other_data else 1 for element in actual_data]
        new_predicted_data = [0 if element in other_data else 1 for element in predicted_data]

        roc_auc = roc_auc_score(new_data, new_predicted_data, average=average)
        roc_auc_dictionary[each_data] = roc_auc

    return roc_auc_dictionary
