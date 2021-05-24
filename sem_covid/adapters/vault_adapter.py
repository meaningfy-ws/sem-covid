# import hvac
# import json
#
#
# class VaultAdapter:
#
#     def __init__(self,
#                  vault_addr: str,
#                  vault_token: str,
#                  secret_mount: str
#                  ):
#         self._client = hvac.Client(url=vault_addr, token=vault_token)
#         self._secret_mount = secret_mount
#
#     def load_secrets_for_path(self, path: str) -> dict:
#         secret_response = self._client.secrets.kv.v2.read_secret_version(path=path, mount_point=self._secret_mount)
#         result_data_str = str(secret_response['data']['data'])
#         result_data_json = result_data_str.replace("'", "\"")
#         result_data = json.loads(result_data_json)
#         return result_data
#
#     def load_secrets_for_paths(self, paths: list) -> dict:
#         result_secrets_dict = {}
#         for path in paths:
#             result_secrets_dict.update(self.load_secrets_for_path(path))
#         return result_secrets_dict
