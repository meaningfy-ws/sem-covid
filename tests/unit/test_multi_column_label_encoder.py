
from ml_experiments.services.sc_wrangling.value_replacement import MultiColumnLabelEncoder


def test_replace_column_labels_with_label_encoder(transformed_pwdb_dataframe):
    assert len(transformed_pwdb_dataframe) == 2
    pwdb_label_encoder = MultiColumnLabelEncoder(
        columns=['Category', 'Subcategory', 'Type of measure']).fit_transform(transformed_pwdb_dataframe)
    assert 'Category' in pwdb_label_encoder
    assert 'Subcategory' in pwdb_label_encoder
    assert 'Type of measure' in pwdb_label_encoder
    assert 0 in pwdb_label_encoder['Category']
    assert 0 in pwdb_label_encoder['Subcategory']
    assert 0 in pwdb_label_encoder['Type of measure']
    assert "Income protection beyond short-time work" not in pwdb_label_encoder['Category']
    assert "Extensions of  income support to workers not covered by any kind of protection scheme" \
        not in pwdb_label_encoder['Subcategory']
    assert "Legislations or other statutory regulations" not in pwdb_label_encoder['Type of measure']
