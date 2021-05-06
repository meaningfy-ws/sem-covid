from sem_covid.adapters.vault_adapter import VaultAdapter
from sem_covid import config


def test_vault_adapter():
    vault_adapter = VaultAdapter(config.VAULT_ADDR, config.VAULT_TOKEN)
    secrets = vault_adapter.get_all_secrets()
    assert type(secrets) == dict
    AIRFLOW_GID = vault_adapter.get_secret_value('AIRFLOW_GID')
    assert AIRFLOW_GID == '50000'
