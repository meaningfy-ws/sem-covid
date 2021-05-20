from tests.unit.test_store.fake_storage import FakeObjectStore


def test_object_store():
    obj_store = FakeObjectStore()
    assert obj_store is not None
    object_content = "Hello Bob!"
    obj_store.put_object(object_name="Bob", content=object_content)
    tmp_object = obj_store.get_object(object_name="Bob")
    assert tmp_object == object_content
    tmp_object = obj_store.get_object("Alice")
    assert tmp_object is None
    obj_store.clear_storage(object_name_prefix="b")
    tmp_object = obj_store.get_object(object_name="Bob")
    assert tmp_object is not None
    obj_store.clear_storage(object_name_prefix="B")
    tmp_object = obj_store.get_object(object_name="Bob")
    assert tmp_object is None
    object_content = "Test list of objects"
    obj_store.put_object(object_name="B1", content=object_content)
    obj_store.put_object(object_name="B2", content=object_content)
    obj_store.put_object(object_name="B3", content=object_content)
    objects = obj_store.list_objects(object_name_prefix="B")
    for obj in objects:
        assert obj == object_content
    obj_store.clear_storage(object_name_prefix="B")
    objects = obj_store.list_objects(object_name_prefix="B")
    assert len(objects) == 0
