from sem_covid.services.model_registry import ClassificationModel


def test_model_registry():
    assert ClassificationModel.PWDB_BUSINESSES is not None
    assert ClassificationModel.PWDB_WORKERS is not None
    assert ClassificationModel.PWDB_CATEGORY is not None
    assert ClassificationModel.PWDB_CITIZENS is not None
    assert ClassificationModel.PWDB_SUBCATEGORY is not None
    assert ClassificationModel.PWDB_TARGET_GROUPS is not None
    assert ClassificationModel.PWDB_TYPE_OF_MEASURE is not None
    assert ClassificationModel.pwdb_by_class_name('workers') is not None
    assert ClassificationModel.pwdb_by_class_name('Orange') is None
