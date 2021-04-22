#!/usr/bin/python3

# cellar_adapter.py
# Date:  30/01/2021
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com

import hashlib
import json
import logging
import pathlib
from functools import partial
from multiprocessing import Pool, cpu_count
import requests

logger = logging.getLogger(__name__)


def enrich_policy_watch(covid19db_json_location: pathlib.Path, covid19_enriched_fragments_output_path: pathlib.Path):
    with open(covid19db_json_location, encoding='utf-8') as covid19db:
        covid19json = json.loads(covid19db.read())

    list_count = len(covid19json)
    current_item = 0

    for field_data in covid19json:
        current_item += 1
        logger.info('[' + str(current_item) + ' / ' + str(list_count) + '] - ' + field_data['fieldData']['title'])
        # map.pool has SERIOUS LOCK/DEADLOCK ISSUES ! Remove the code and make it sequential !
        with Pool(processes=cpu_count()) as pool:
            field_data['portalData']['sources'] = pool.map(partial(__download_source),
                                                           field_data['portalData']['sources'])
            pool.close()
            pool.join()

            for source in field_data['portalData']['sources']:
                with open(covid19_enriched_fragments_output_path / hashlib.sha256(
                        source['sources::url'].encode('utf-8')).hexdigest(), 'w') as enriched_fragment_file:
                    json.dump(source, enriched_fragment_file)


def __download_source(source):
    try:
        url = source['sources::url'] if source['sources::url'].startswith('http') else (
                'http://' + source['sources::url'])
        request = requests.get(url, allow_redirects=True)

        source['content'] = str(request.content)
    except Exception as ex:
        source['failure_reason'] = str(ex)

    return source
