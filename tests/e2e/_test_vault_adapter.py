import os

from sem_covid.adapters.vault_secrets_store import VaultSecretsStore
from sem_covid import config


def test_vault_adapter():
    assert config.VAULT_ADDR == "http://srv.meaningfy.ws:8200"
    vault_adapter = VaultSecretsStore(config.VAULT_ADDR, config.VAULT_TOKEN, "mfy")
    secrets = vault_adapter.get_secrets("air-flow")
    assert type(secrets) == dict
