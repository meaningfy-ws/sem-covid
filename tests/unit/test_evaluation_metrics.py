from sklearn import svm

from sem_covid.services.sc_wrangling.evaluation_metrics import model_evaluation_metrics, calculate_roc_auc_multiclass


def test_model_evaluation_metrics(sklearn_train_test_data):
    svm_algorithm = svm.SVC()
    svm_algorithm.fit(sklearn_train_test_data['x_train'], sklearn_train_test_data['y_train'])
    prediction = svm_algorithm.predict(sklearn_train_test_data['x_test'])
    evaluation = model_evaluation_metrics(sklearn_train_test_data['y_test'], prediction)

    assert dict == type(evaluation)
    assert 1.0 == evaluation['Accuracy']
    assert 1.0 == evaluation['Precision']
    assert 1.0 == evaluation['Recall']
    assert 1.0 == evaluation['F1-Score']
    assert 0.0 == evaluation['Mean Absolute Error']
    assert 0.0 == evaluation['Mean Squared Error']


def test_calculate_roc_auc_multiclass(sklearn_train_test_data):
    svm_algorithm = svm.SVC()
    svm_algorithm.fit(sklearn_train_test_data['x_train'], sklearn_train_test_data['y_train'])
    prediction = svm_algorithm.predict(sklearn_train_test_data['x_test'])
    evaluation = calculate_roc_auc_multiclass(sklearn_train_test_data['y_test'], prediction)

    assert dict == type(evaluation)
    assert 3 == len(evaluation)
    assert 1.0 == evaluation[0]
    assert 1.0 == evaluation[1]
    assert 1.0 == evaluation[2]




