#!/usr/bin/python3

# documents.py
# Date:  15/01/2021
# Author: Mihai Coșleț
# Email: coslet.mihai@gmail.com 

""" """
import logging
from pathlib import Path

import requests

logger = logging.getLogger('lam-fetcher')

TYPES = {
    'html': 'TXT/HTML',
    'pdf': 'TXT/PDF',
    'formex': 'TXT/FORMEX'
}


def retrieve_document_by_celex_id(path_to_save: str, celex_id: str, language: str = 'EN', type: str = 'formex'):
    logger.debug(f'start retrieving {celex_id} in {language} with {type} format.')

    url = f'https://eur-lex.europa.eu/legal-content/{language}/{TYPES[type]}/?uri=CELEX:{celex_id}'

    response = requests.get(url)
    if response.status_code != 200:
        logger.debug(f'request on {celex_id} returned {response.status_code}')
        raise ValueError(f'request returned {response.status_code}')

    file_location = Path(path_to_save) / f'{celex_id}-{language}.{type}'
    with open(file_location, 'wb') as file:
        file.write(response.content)

    logger.debug(f'finish retrieving {celex_id} in {language} with {type} format.')
