import copy
import io
import json
import pathlib
from http.client import HTTPResponse
from typing import Any, Optional, Union, Collection, MutableMapping, List

from elasticsearch import Elasticsearch
from es_pandas import es_pandas

from sem_covid.adapters.abstract_store import *
from minio import Minio

TEST_DATA_FOLDER = pathlib.Path(__file__).parent.parent.parent / "test_data"


class FakeMinioObject:

    def __init__(self, object_name: str, content):
        self.object_name = object_name
        self.content = content


class FakeHTTPMinioResponse:
    def __init__(self, content: io.BytesIO = None):
        self.content = content

    def read(self):
        if self.content is not None:
            return self.content.read()
        return self.content

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass


class FakeMinioClient(Minio):

    def __init__(self):
        self.storage = dict()
        self._http = dict()

    def put_object(self, bucket_name, object_name, data, length, content_type="application/octet-stream", metadata=None,
                   sse=None, progress=None, part_size=0, num_parallel_uploads=3, tags=None, retention=None,
                   legal_hold=False):
        self.storage[bucket_name][object_name] = FakeMinioObject(object_name, data)

    def remove_objects(self, bucket_name, delete_object_list, bypass_governance_mode=False):
        for tmp_object in delete_object_list:
            self.storage[bucket_name].pop(tmp_object._name, None)
        return list()

    def make_bucket(self, bucket_name, location=None, object_lock=False):
        self.storage[bucket_name] = dict()

    def get_object(self, bucket_name, object_name, offset=0, length=0, request_headers=None, ssec=None, version_id=None,
                   extra_query_params=None):
        if bucket_name in self.storage.keys():
            if object_name in self.storage[bucket_name].keys():
                return FakeHTTPMinioResponse(self.storage[bucket_name][object_name].content)
        return FakeHTTPMinioResponse()

    def bucket_exists(self, bucket_name):
        return bucket_name in self.storage.keys()

    def list_objects(self, bucket_name, prefix=None, recursive=False, start_after=None, include_user_meta=False,
                     include_version=False, use_api_v1=False):
        result = list()
        if prefix is not None:
            for key in self.storage[bucket_name].keys():
                str_key = str(key)
                if str_key.startswith(prefix):
                    result.append(self.storage[bucket_name][key])
        else:
            result = list(self.storage[bucket_name].values())
        return result


class FakeObjectStoreObject(object):
    """
        This is a fake class to mimic minio.datatypes.Object whic saccounts
        for object metadata including object_name used in our code
    """

    def __init__(self, object_name):
        self.object_name = object_name

    def __str__(self):
        return self.object_name

    def __repr__(self):
        return self.__str__()


class FakeObjectStore(ObjectStoreABC):
    """

    """

    def __init__(self):
        self._objects = dict()

    def empty_bucket(self, object_name_prefix=None):
        tmp_dict = dict.fromkeys(self._objects.keys(), [])
        for key in tmp_dict.keys():
            str_key = str(key)
            if str_key.startswith(object_name_prefix):
                del self._objects[key]

    def put_object(self, object_name: str, content):
        self._objects[object_name] = content

    def get_object(self, object_name: str):
        if object_name in self._objects.keys():
            return self._objects[object_name]
        else:
            return None

    def list_objects(self, object_name_prefix: str) -> List:
        return [
            FakeObjectStoreObject(key)
            for key in self._objects.keys()
            if str(key).startswith(object_name_prefix)
        ]

class FakeSecretsStore(SecretsStoreABC):
    def get_secrets(self, path: str) -> dict:
        secrets = {
            "secret_path1":
                {
                    "secret1": "white",
                    "secret2": "black"
                },
            "secret_path2":
                {
                    "secret3": "orange",
                    "secret4": "green"
                }

        }
        return secrets[path]


class FakeElasticSearchClient(Elasticsearch):

    def search(self, *, body: Optional[Any] = ..., index: Optional[Any] = ..., doc_type: Optional[Any] = ...,
               _source: Optional[Any] = ..., _source_excludes: Optional[Any] = ...,
               _source_includes: Optional[Any] = ..., allow_no_indices: Optional[Any] = ...,
               allow_partial_search_results: Optional[Any] = ..., analyze_wildcard: Optional[Any] = ...,
               analyzer: Optional[Any] = ..., batched_reduce_size: Optional[Any] = ...,
               ccs_minimize_roundtrips: Optional[Any] = ..., default_operator: Optional[Any] = ...,
               df: Optional[Any] = ..., docvalue_fields: Optional[Any] = ..., expand_wildcards: Optional[Any] = ...,
               explain: Optional[Any] = ..., from_: Optional[Any] = ..., ignore_throttled: Optional[Any] = ...,
               ignore_unavailable: Optional[Any] = ..., lenient: Optional[Any] = ...,
               max_concurrent_shard_requests: Optional[Any] = ..., min_compatible_shard_node: Optional[Any] = ...,
               pre_filter_shard_size: Optional[Any] = ..., preference: Optional[Any] = ..., q: Optional[Any] = ...,
               request_cache: Optional[Any] = ..., rest_total_hits_as_int: Optional[Any] = ...,
               routing: Optional[Any] = ..., scroll: Optional[Any] = ..., search_type: Optional[Any] = ...,
               seq_no_primary_term: Optional[Any] = ..., size: Optional[Any] = ..., sort: Optional[Any] = ...,
               stats: Optional[Any] = ..., stored_fields: Optional[Any] = ..., suggest_field: Optional[Any] = ...,
               suggest_mode: Optional[Any] = ..., suggest_size: Optional[Any] = ..., suggest_text: Optional[Any] = ...,
               terminate_after: Optional[Any] = ..., timeout: Optional[Any] = ..., track_scores: Optional[Any] = ...,
               track_total_hits: Optional[Any] = ..., typed_keys: Optional[Any] = ..., version: Optional[Any] = ...,
               pretty: Optional[bool] = ..., human: Optional[bool] = ..., error_trace: Optional[bool] = ...,
               format: Optional[str] = ..., filter_path: Optional[Union[str, Collection[str]]] = ...,
               request_timeout: Optional[Union[int, float]] = ..., ignore: Optional[Union[int, Collection[int]]] = ...,
               opaque_id: Optional[str] = ..., params: Optional[MutableMapping[str, Any]] = ...,
               headers: Optional[MutableMapping[str, str]] = ...) -> Any:
        return "FakeSearchResult"

    def get(self, index: Any, id: Any, *, doc_type: Optional[Any] = ..., _source: Optional[Any] = ...,
            _source_excludes: Optional[Any] = ..., _source_includes: Optional[Any] = ...,
            preference: Optional[Any] = ..., realtime: Optional[Any] = ..., refresh: Optional[Any] = ...,
            routing: Optional[Any] = ..., stored_fields: Optional[Any] = ..., version: Optional[Any] = ...,
            version_type: Optional[Any] = ..., pretty: Optional[bool] = ..., human: Optional[bool] = ...,
            error_trace: Optional[bool] = ..., format: Optional[str] = ...,
            filter_path: Optional[Union[str, Collection[str]]] = ...,
            request_timeout: Optional[Union[int, float]] = ..., ignore: Optional[Union[int, Collection[int]]] = ...,
            opaque_id: Optional[str] = ..., params: Optional[MutableMapping[str, Any]] = ...,
            headers: Optional[MutableMapping[str, str]] = ...) -> Any:
        return "FakeGetResult"

    def index(self, index: Any, *, body: Any, doc_type: Optional[Any] = ..., id: Optional[Any] = ...,
              if_primary_term: Optional[Any] = ..., if_seq_no: Optional[Any] = ..., op_type: Optional[Any] = ...,
              pipeline: Optional[Any] = ..., refresh: Optional[Any] = ..., require_alias: Optional[Any] = ...,
              routing: Optional[Any] = ..., timeout: Optional[Any] = ..., version: Optional[Any] = ...,
              version_type: Optional[Any] = ..., wait_for_active_shards: Optional[Any] = ...,
              pretty: Optional[bool] = ..., human: Optional[bool] = ..., error_trace: Optional[bool] = ...,
              format: Optional[str] = ..., filter_path: Optional[Union[str, Collection[str]]] = ...,
              request_timeout: Optional[Union[int, float]] = ..., ignore: Optional[Union[int, Collection[int]]] = ...,
              opaque_id: Optional[str] = ..., params: Optional[MutableMapping[str, Any]] = ...,
              headers: Optional[MutableMapping[str, str]] = ...) -> Any:
        return "FakeIndexResult"


class FakeEsPandasClient(es_pandas):

    def __init__(self):
        self.store = FakeIndexStore()
        self.es = FakeElasticSearchClient()

    def to_es(self, df, index, doc_type=None, use_index=False, show_progress=True, success_threshold=0.9,
              _op_type='index', use_pandas_json=False, date_format='iso', **kwargs):
        self.store.put_dataframe(index_name=index, content=df)

    def to_pandas(self, index, query_rule=None, heads=[], dtype={}, infer_dtype=False, show_progress=True, **kwargs):
        return self.store.get_dataframe(index_name=index)


class FakeIndexStore(IndexStoreABC):

    def create_index(self, index_name: str, index_mappings: dict, exist_ok=True):
        pass

    def __init__(self):
        self._store = dict()

    def index(self, index_name, document_id, document_body):
        pass

    def get_document(self, index_name: str, document_id: str):
        pass

    def search(self, index_name: str, query: str, exclude_binary_source: bool = True):
        pass

    def get_dataframe(self, index_name: str) -> pd.DataFrame:
        if index_name in self._store:
            return self._store[index_name]
        else:
            return None

    def put_dataframe(self, index_name: str, content: pd.DataFrame):
        self._store[index_name] = content

    def dump(self, index_name: str, file_name: str, local_path: pathlib.Path = None,
             remote_store: ObjectStoreABC = None):
        pass


class FakeFeatureStore(FeatureStoreABC):

    def __init__(self):
        self._store = dict()

    def get_features(self, features_name: str) -> pd.DataFrame:
        if features_name in self._store:
            return self._store[features_name]
        else:
            return None

    def put_features(self, features_name: str, content: pd.DataFrame):
        self._store[features_name] = content


class FakeTripleStore(TripleStoreABC):
    def with_query(self, sparql_query: str, substitution_variables: dict = None,
                   sparql_prefixes: str = "") -> 'TripleStoreABC':
        return self

    def with_query_from_file(self, sparql_query_file_path: str, substitution_variables: dict = None,
                             prefixes: str = "") -> 'TripleStoreABC':
        return self

    def get_dataframe(self) -> pd.DataFrame:
        path = TEST_DATA_FOLDER / "eu_cellar_covid_fragments" / "unified_eu_cellar_fragment.json"
        json_eu_cellar_covid = json.loads(path.read_bytes())

        return pd.DataFrame(data=json_eu_cellar_covid)
