#!/usr/bin/python3

# test_config.py
# Date:  22/04/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import os

from sem_covid.config_resolver import BaseConfig
from tests.unit.conftest import FakeBaseConfig


def test_config():
    if "test_config" in os.environ:
        del os.environ["test_config"]
    assert "test_config" not in os.environ
    assert BaseConfig.find_value(default_value="bubu") == "bubu"
    os.environ["test_config"] = "foo"
    assert BaseConfig.find_value(default_value="bubu") == "foo"
    del os.environ["test_config"]
    assert "test_config" not in os.environ


def test_fake_base_config():
    if "PWDB_XXX" in os.environ:
        del os.environ["PWDB_XXX"]
    assert "PWDB_XXX" not in os.environ
    config = FakeBaseConfig()
    assert config.PWDB_XXX == "baubau"
    os.environ["PWDB_XXX"] = "foo"
    config1 = FakeBaseConfig()
    assert config1.PWDB_XXX == "foo"
    del os.environ["PWDB_XXX"]
    assert "PWDB_XXX" not in os.environ
