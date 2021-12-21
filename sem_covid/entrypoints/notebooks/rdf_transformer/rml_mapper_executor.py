from abc import ABC, abstractmethod
import json
import requests as req
from pathlib import Path
from typing import List
class RMLMapperABC(ABC):

    @abstractmethod
    def transform(self, rml_rule: str, sources: dict) -> str:
        pass

class RMLMapper(RMLMapperABC):

    def __init__(self,
                rml_mapper_url: str
                ):
        self.rml_mapper_url = rml_mapper_url
    
    def transform(self, rml_rule: str, sources: dict)-> str:
        rml_mapper_query = {"rml": rml_rule, "sources": sources}
        #print(rml_mapper_query)
        rml_mapper_result = req.post(self.rml_mapper_url, json = rml_mapper_query)
        if rml_mapper_result.ok:
            return json.loads(rml_mapper_result.text)['output']
        else:
            print(rml_mapper_result)
            return None


def pack_data_sources(source_path: Path)->dict:
    sources = { str(file_path.name) : str(file_path.read_text())
                for file_path in list(source_path.glob("**/*"))}
    return sources


RML_MAPPER_URL = "http://srv.meaningfy.ws:4000/execute"
RML_RULE_FILE_NAME = "ds_unified_dataset.ttl"
DATA_SOURCES_PATH = Path(__file__).resolve().parent/Path("./sources/")


rml_mapper = RMLMapper(rml_mapper_url=RML_MAPPER_URL)

rml_rule = (Path(__file__).resolve().parent/Path(f"./rml_rules/{RML_RULE_FILE_NAME}")).read_text()

sources = pack_data_sources(DATA_SOURCES_PATH)

print(sources.keys())
#print(sources.keys())
# for key in sources.keys():
#     print(key)
#     print(sources[key])

rdf_result = rml_mapper.transform(rml_rule=rml_rule, sources = pack_data_sources(DATA_SOURCES_PATH))

assert rdf_result is not None
(Path(__file__).resolve().parent/Path("./results/test_result.ttl")).write_text(rdf_result)



