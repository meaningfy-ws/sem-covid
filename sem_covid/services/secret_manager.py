from sem_covid.adapters.vault_secrets_storage import VaultSecretsStorage

SECRET_PATHS = ['air-flow', 'elastic-search', 'jupyter-notebook', 'min-io', 'ml-flow', 'sem-covid',
                'sem-covid-infra']
SECRET_MOUNT = 'mfy'


def get_vault_secret(secret_key: str, default_value: str = None):
    from sem_covid import config
    vault_client = VaultSecretsStorage(config.VAULT_ADDR, config.VAULT_TOKEN, SECRET_MOUNT)
    secrets_dict = {}
    for path in SECRET_PATHS:
        secrets_dict.update(vault_client.get_secrets(path))
    if secret_key in secrets_dict.keys():
        return secrets_dict[secret_key]
    else:
        return default_value
