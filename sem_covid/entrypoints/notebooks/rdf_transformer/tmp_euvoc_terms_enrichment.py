from pathlib import Path
import pandas as pd
import json

EUVOC_TERMS_MAPPING = [("corporate_body.csv", "eu_cellar_author_labels"),
                       ("resource_type.csv", "eu_cellar_resource_type_labels"),
                       ("subject_matter.csv", "eu_cellar_subject_matter_labels"),
                       ('country.csv', "country")
                       ]


def enrich_with_euvoc_terms(euvoc_terms_file: str, column_name: str):
    df = pd.read_csv(Path(__file__).resolve().parent /
                     Path(f"./euvoc_terms/{euvoc_terms_file}"))
    data_file_path = Path(__file__).resolve().parent / \
        Path(f"./data/{column_name}.json")
    data = json.loads(data_file_path.read_text())
    records = data[column_name]
    remove_indexes = []
    for index in range(0, len(records)):
        values = df[df['label'] == records[index]['name']]['uri'].values
        if len(values):
            records[index]['uri'] = values[0]
        else:
            remove_indexes.append(index)
    print(len(records))
    for remove_index in sorted(remove_indexes, reverse=True):
        records.pop(remove_index)
    print(len(records))
    data[column_name] = records
    data_file_path.write_text(json.dumps(data))


for euvoc_terms_file, column_name in EUVOC_TERMS_MAPPING:
    enrich_with_euvoc_terms(
        euvoc_terms_file=euvoc_terms_file, column_name=column_name)
