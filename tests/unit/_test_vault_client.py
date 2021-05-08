import hvac
import os
import json
from sem_covid import config


def test_vault_client():
    assert 'VAULT_ADDR' in os.environ
    assert 'VAULT_TOKEN' in os.environ
    client = hvac.Client(
        url=config.VAULT_ADDR,
        token=config.VAULT_TOKEN
    )
    assert client.is_authenticated()
    secret_version_response = client.secrets.kv.v2.read_secret_version(
        path='air-flow',
        mount_point='mfy'
    )
    data_json = str(secret_version_response['data']['data'])
    data_json = data_json.replace("'", "\"")
    data = json.loads(data_json)
    assert type(data) == dict
