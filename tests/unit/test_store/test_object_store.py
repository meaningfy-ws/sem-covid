from sem_covid.adapters.minio_object_store import MinioObjectStore
from tests.fake_storage import FakeObjectStore, FakeMinioClient


def test_fake_object_store():
    obj_store = FakeObjectStore()
    assert obj_store is not None
    object_content = "Hello Bob!"
    obj_store.put_object(object_name="Bob", content=object_content)
    tmp_object = obj_store.get_object(object_name="Bob")
    assert tmp_object == object_content
    tmp_object = obj_store.get_object("Alice")
    assert tmp_object is None
    obj_store.empty_bucket(object_name_prefix="b")
    tmp_object = obj_store.get_object(object_name="Bob")
    assert tmp_object is not None
    obj_store.empty_bucket(object_name_prefix="B")
    tmp_object = obj_store.get_object(object_name="Bob")
    assert tmp_object is None
    object_content = "Test list of objects"
    obj_store.put_object(object_name="B1", content=object_content)
    obj_store.put_object(object_name="B2", content=object_content)
    obj_store.put_object(object_name="B3", content=object_content)
    objects = obj_store.list_objects(object_name_prefix="B")
    for key, value in obj_store._objects.items():
        assert 'B' in key
        assert object_content in value
    obj_store.empty_bucket(object_name_prefix="B")
    objects = obj_store.list_objects(object_name_prefix="B")
    assert len(objects) == 0


def test_minio_object_store():
    minio_client = FakeMinioClient()
    bucket_name = "test"
    minio_store = MinioObjectStore(bucket_name, minio_client)
    assert minio_store.get_object("no_object") is None
    content = "Hello World"
    minio_store.put_object("b1", content)
    result = minio_store.get_object("b1")
    assert type(result) == bytes
    result = result.decode('utf-8')
    assert content == result
    content = "Orange"
    minio_store.put_object("b2", content)
    list_objects = minio_store.list_objects("b")
    minio_store.empty_bucket("b")
    assert minio_store.get_object("b1") is None
    assert minio_store.get_object("b2") is None
