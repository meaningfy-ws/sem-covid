import hvac
import json


class VaultAdapter:
    __secret_paths: list = ['air-flow', 'elastic-search', 'jupyter-notebook', 'min-io', 'ml-flow', 'sem-covid',
                            'sem-covid-infra']
    __secret_mount: str = 'mfy'
    __secrets_cache: dict = None

    def __init__(self,
                 vault_addr: str = None,
                 vault_token: str = None
                 ):
        self.__vault_addr = vault_addr
        self.__vault_token = vault_token

    def __load_secrets_for_path(self, path: str) -> dict:

        from sem_covid import config

        if self.__vault_addr is None:
            self.__vault_addr = config.VAULT_ADDR
        if self.__vault_token is None:
            self.__vault_token = config.VAULT_TOKEN

        self.__client = hvac.Client(url=self.__vault_addr, token=self.__vault_token)

        secret_response = self.__client.secrets.kv.v2.read_secret_version(path=path, mount_point=self.__secret_mount)
        result_data_str = str(secret_response['data']['data'])
        result_data_json = result_data_str.replace("'", "\"")
        result_data = json.loads(result_data_json)
        return result_data

    def __load_secrets_in_cache(self):
        local_secrets_cache = {}
        for path in self.__secret_paths:
            local_secrets_cache.update(self.__load_secrets_for_path(path))
        self.__secrets_cache = local_secrets_cache

    def get_secret_value(self, secret_name: str, default: str = None) -> str:
        if self.__secrets_cache is None:
            self.__load_secrets_in_cache()

        if secret_name in self.__secrets_cache.keys():
            return self.__secrets_cache[secret_name]
        else:
            return default

    def get_all_secrets(self) -> dict:
        if self.__secrets_cache is None:
            self.__load_secrets_in_cache()
        return self.__secrets_cache
