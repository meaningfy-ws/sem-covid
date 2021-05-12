from sem_covid.adapters.vault_secrets_storage import VaultSecretsStorage
from sem_covid import config


def test_vault_adapter():
    vault_adapter = VaultSecretsStorage(config.VAULT_ADDR, config.VAULT_TOKEN, "mfy")
    secrets = vault_adapter.get_secrets("air-flow")
    assert type(secrets) == dict
