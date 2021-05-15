import hvac
import json

from sem_covid.adapters.abstract_store import SecretsStoreABC


class VaultSecretsStore(SecretsStoreABC):

    def __init__(self,
                 vault_addr: str,
                 vault_token: str,
                 secret_mount: str
                 ):
        self._client = hvac.Client(url=vault_addr, token=vault_token)
        self._secret_mount = secret_mount

    def get_secrets(self, path: str) -> dict:
        secret_response = self._client.secrets.kv.v2.read_secret_version(path=path, mount_point=self._secret_mount)
        result_data_str = str(secret_response['data']['data'])
        result_data_json = result_data_str.replace("'", "\"")
        result_data = json.loads(result_data_json)
        return result_data

