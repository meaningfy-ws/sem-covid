
from sem_covid.services.sc_wrangling.value_replacement import MultiColumnLabelEncoder


def test_replace_column_labels_with_label_encoder(transformed_pwdb_dataframe):
    assert len(transformed_pwdb_dataframe) == 2
    pwdb_label_encoder = MultiColumnLabelEncoder(
        columns=['category', 'subcategory', 'type_of_measure']).fit_transform(transformed_pwdb_dataframe)
    assert 'category' in pwdb_label_encoder
    assert 'subcategory' in pwdb_label_encoder
    assert 'type_of_measure' in pwdb_label_encoder
    assert 0 in pwdb_label_encoder['category']
    assert 0 in pwdb_label_encoder['subcategory']
    assert 0 in pwdb_label_encoder['type_of_measure']
    assert "Income protection beyond short-time work" not in pwdb_label_encoder['category']
    assert "Extensions of  income support to workers not covered by any kind of protection scheme" \
        not in pwdb_label_encoder['subcategory']
    assert "Legislations or other statutory regulations" not in pwdb_label_encoder['type_of_measure']
