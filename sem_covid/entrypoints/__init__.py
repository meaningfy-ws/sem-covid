#!/usr/bin/python3

# __init__.py
# Date:  18/03/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
from datetime import datetime, timedelta
from typing import Union

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

from resources import sparql_queries

DEFAULT_DAG_ARGUMENTS = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2021, 2, 22),
    "email": ["info@meaningfy.ws"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=3600)
}


def dag_name(category: str,
             name: str,
             role: str = None,
             version_major: Union[int, None] = 0,
             version_minor: int = None,
             version_patch: int = None,
             versioning: bool = True) -> str:
    """
        A function unifying the naming conventions across all DAGs.

        Versioning option 1: Semantic versioning: provide major, minor and path numbers
        Versioning option 2: Evolutive versioning: do NOT provide major version, then the dateStamp will be used as a version
        Versioning option 3: No versioning
    """
    semantic_version = f"{version_major if version_major is not None else 0}." \
                       f"{version_minor if version_minor is not None else 1}." \
                       f"{version_patch if version_patch is not None else 0}"
    evolutive_version = f"{datetime.today().strftime('%Y-%m-%d')}({version_patch if version_patch else 0})"
    base = f"{category}_{name}_{role}" if role is not None else f"{category}_{name}"
    if versioning:
        if version_major is not None:
            return f"{base}_{semantic_version}"
        else:
            return f"{base}_{evolutive_version}"
    return base


def get_sparql_query(query_file_name: str) -> str:
    """
        get a predefined SPARQL query by reference to file name
    """
    with pkg_resources.path(sparql_queries, query_file_name) as path:
        return str(path)
