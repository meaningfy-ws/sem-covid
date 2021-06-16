#!/usr/bin/python3

# __init__.py
# Date:  18/03/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """


def dag_name(category: str,
             name: str,
             role: str,
             version_major: str = '0',
             version_minor: str = '1',
             version_patch: str = '0') -> str:
    """
        a function unifying the naming conventions across all DAGs
    """
    return f"{category}_{name}_{role}_{version_major}.{version_minor}.{version_patch}"
