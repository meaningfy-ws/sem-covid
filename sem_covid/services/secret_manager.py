from sem_covid.adapters.vault_adapter import VaultAdapter

SECRET_PATHS = ['air-flow', 'elastic-search', 'jupyter-notebook', 'min-io', 'ml-flow', 'sem-covid',
                'sem-covid-infra']
SECRET_MOUNT = 'mfy'


def get_vault_secret(secret_key: str, default_value: str = None):
    from sem_covid import config
    vault_client = VaultAdapter(config.VAULT_ADDR, config.VAULT_TOKEN, SECRET_MOUNT)
    secrets_dict = vault_client.load_secrets_for_paths(SECRET_PATHS)
    if secret_key in secrets_dict.keys():
        return secrets_dict[secret_key]
    else:
        return default_value
