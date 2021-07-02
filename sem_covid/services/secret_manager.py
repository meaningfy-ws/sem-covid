#!/usr/bin/python3

# secret_manager.py
# Date:  01/07/2021
# Author: Stratulat Ștefan

"""
    This module aims to provide easy access to the secrets in Vault.
"""

from sem_covid.adapters.vault_secrets_store import VaultSecretsStore

SECRET_PATHS = ['air-flow', 'elastic-search', 'jupyter-notebook', 'min-io', 'ml-flow', 'sem-covid',
                'sem-covid-infra']
SECRET_MOUNT = 'mfy'


def get_vault_secret(secret_key: str, default_value: str = None):
    """
        This function extracts from the vault the value of a secret based on the name of the secret.
    :param secret_key: the name of the secret sought.
    :param default_value: the default return value in case the secret is not found.
    :return:
    """
    from sem_covid import config
    vault_client = VaultSecretsStore(config.VAULT_ADDR, config.VAULT_TOKEN, SECRET_MOUNT)
    secrets_dict = {}
    for path in SECRET_PATHS:
        secrets_dict.update(vault_client.get_secrets(path))
    if secret_key in secrets_dict.keys():
        return secrets_dict[secret_key]
    else:
        return default_value
