from sem_covid.adapters.vault_adapter import VaultAdapter
from sem_covid import config


def test_vault_adapter():
    vault_adapter = VaultAdapter(config.VAULT_ADDR, config.VAULT_TOKEN, "mfy")
    secrets = vault_adapter.load_secrets_for_path("air-flow")
    assert type(secrets) == dict
