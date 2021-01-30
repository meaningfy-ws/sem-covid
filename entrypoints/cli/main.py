import hashlib
import json
import pathlib
from datetime import datetime
from functools import partial
from multiprocessing import Pool, cpu_count

import requests


def download_source(source):
    download_location = pathlib.Path('resources/policywatch_external_files')
    local_file_name = hashlib.sha256(source['sources::url'].encode('utf-8')).hexdigest()
    try:
        url = source['sources::url'] if source['sources::url'].startswith('http') else (
                'http://' + source['sources::url'])
        request = requests.get(url, allow_redirects=True)

        with open(pathlib.Path(download_location) / str(local_file_name), 'wb') as output_file:
            output_file.write(request.content)
            source['downloaded_to'] = str(local_file_name)
    except Exception as ex:
        source['failure_reason'] = str(ex)

    return source


def enrich_policy_watch():
    with open(pathlib.Path('resources') / 'covid19db.json', encoding='utf-8') as covid19db:
        covid19json = json.loads(covid19db.read())

    list_count = len(covid19json)
    current_item = 0

    for field_data in covid19json:
        current_item += 1
        print('[' + str(current_item) + ' / ' + str(list_count) + '] - ' + field_data['fieldData']['title'])
        with Pool(processes=cpu_count()) as pool:
            field_data['portalData']['sources'] = pool.map(partial(download_source),
                                                           field_data['portalData']['sources'])
            pool.close()
            pool.join()

    with open(pathlib.Path('resources') / 'covid19db_extended.json', 'w') as covid19db_extended:
        json.dump(covid19json, covid19db_extended)


def split_policy_watch():
    with open(pathlib.Path('resources') / 'covid19db_extended.json', encoding='utf-8') as covid19db_extended:
        covid19json_extended = json.loads(covid19db_extended.read())

    list_count = len(covid19json_extended)
    current_item = 0

    for field_data in covid19json_extended:
        current_item += 1
        print('Dumping [' + str(current_item) + ' / ' + str(list_count) + '] - ' + field_data['fieldData']['title'])
        current_filename = str(current_item) + '.json'
        with open(pathlib.Path('resources/policy_watch_field_data_fragments') / current_filename,
                  'w') as enriched_field_data_file:
            json.dump(field_data, enriched_field_data_file)


if __name__ == "__main__":
    print(str(datetime.now()) + " - starting downloading the EU’s PolicyWatch DB for Covid19 (JSON)...")
    enrich_policy_watch()
    split_policy_watch()
    print(str(datetime.now()) + " - done.")
