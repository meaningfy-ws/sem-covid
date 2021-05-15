#!/usr/bin/python3

# test_config.py
# Date:  22/04/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import os

from tests.unit.conftest import FakeConfigResolver


def test_config():
    if "test_config" in os.environ:
        del os.environ["test_config"]
    assert "test_config" not in os.environ
    assert FakeConfigResolver.config_resolve(default_value="bubu") == "bubu"
    os.environ["test_config"] = "foo"
    assert FakeConfigResolver.config_resolve(default_value="bubu") == "foo"
    del os.environ["test_config"]
    assert "test_config" not in os.environ


def test_fake_base_config():
    if "PWDB_XXX" in os.environ:
        del os.environ["PWDB_XXX"]
    assert "PWDB_XXX" not in os.environ
    config = FakeConfigResolver()
    assert config.PWDB_XXX == "baubau"
    os.environ["PWDB_XXX"] = "foo"
    config1 = FakeConfigResolver()
    assert config1.PWDB_XXX == "foo"
    del os.environ["PWDB_XXX"]
    assert "PWDB_XXX" not in os.environ
