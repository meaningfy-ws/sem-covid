import json
import logging
from pathlib import Path

from pytest_bdd import scenario, given, when, then

logger = logging.getLogger(__name__)


@scenario(
    "indexes.feature",
    "PWDB Index Search",
    example_converters=dict(query=str, result_count=int, fields_csv=str)
)
def test_outlined():
    pass


@given('I have the query <query_file>', target_fixture="given_i_have_the_query")
def given_i_have_the_query(query_file, scenario_context, elasticsearch_client):
    scenario_context["query_file"] = query_file


@then("the result count is <result_count>")
def the_result_count_is(result_count, scenario_context):
    assert scenario_context["hits"] == result_count


@when("I run the query against the index")
def i_run_the_query_against_the_index(scenario_context, elasticsearch_client):
    with open(Path(scenario_context["test_data_directory"]) / Path(
            scenario_context["query_file"])) as json_file:
        payload = json.load(json_file)

    result = elasticsearch_client.search(index=scenario_context["index_name"], body=payload)
    scenario_context["hits"] = int(result["hits"]["total"]["value"])
