from sklearn.metrics import (confusion_matrix, f1_score, precision_score, accuracy_score,
                             recall_score, mean_squared_error, mean_absolute_error)

import pandas as pd

class EvaluationMetrics:
    def __init__(self, actual, prediction):
        self.actual = actual
        self.prediction = prediction

    def confusion_matrix(self):
        matrix = confusion_matrix(self.actual, self.prediction)
        return matrix

    def evaluation(self):
        accuracy = accuracy_score(self.actual, self.prediction)
        precision = precision_score(self.actual, self.prediction, average="macro")
        recall = recall_score(self.actual, self.prediction, average="macro")
        f1 = f1_score(self.actual, self.prediction, average="macro")
        mae = mean_absolute_error(self.actual, self.prediction)
        mse = mean_squared_error(self.actual, self.prediction)

        evaluate_metrics = pd.DataFrame({'Evaluation Metrics': ['Accuracy', 'Precission', 'Recall',
                                                                'F1 Score', 'Mean Absolute Error',
                                                                'Mean Squared Error'],
                                         'Category': [accuracy, precision, recall, f1, mae, mse]})

        return evaluate_metrics


