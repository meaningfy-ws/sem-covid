import json

from src.pwdb_transformer import transform_json_to_csv


def test_transform_json_to_csv_number_of_columns_and_rows(tmpdir):
    JSON = [{'fieldData': {'title': 'Hardship case fund: Safety net for self-employed',
                           'title_nationalLanguage': 'hdadsa'}}]

    transformation_rules = '''{
            "Title": .fieldData.title,
            "Title (national language)": .fieldData.title_nationalLanguage
            }'''

    file = tmpdir.join("test_JSON.json")
    file.write(json.dumps(JSON))

    transformer = transform_json_to_csv(file, transformation_rules)

    expected_list = ['Title', 'Title (national language)']
    expected_number_of_rows = 2

    df_rows = transformer.count()
    df_columns = transformer.columns

    # compare number of rows
    assert len(df_rows) == expected_number_of_rows

    # compare number of columns
    assert len(df_columns) == len(expected_list)
    assert all([a == b for a, b in zip(df_columns, expected_list)])
