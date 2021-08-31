from tests.fake_storage import FakeSecretsStore


def test_secrets_store():
    secrets_store = FakeSecretsStore()
    secrets = secrets_store.get_secrets("secret_path1")
    assert type(secrets) == dict
    assert secrets["secret1"] == "white"
    assert secrets["secret2"] == "black"
    assert "secret3" not in secrets
