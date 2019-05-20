
import pytest

from txtferret._config import (
    _load_config,
    _load_default_config,
    load_config,
    _add_user_config_file,
    save_config,
    subset_check,
    validate_config,
)


def test_load_default_config():
    config_string = """
    settings:
      setting1: value1
      setting2: value2
    """
    config_dict = {"settings": {"setting1": "value1", "setting2": "value2"}}
    assert _load_default_config(config_string=config_string) == config_dict

# TODO: Test for actual yaml file load.

def test_subset_check_it_is_subset():
    rv = subset_check(subset={"hello"}, set_={"hello", "world"})
    assert rv == True, "Return value should be True."
    assert isinstance(rv, bool), "Return value should be bool."


def test_subset_check_it_is_subset_they_are_the_same():
    rv = subset_check(subset={"hello", "world"}, set_={"hello", "world"})
    assert rv == True, "Return value should be True."
    assert isinstance(rv, bool), "Return value should be bool."


def test_subset_check_is_not_subset():
    rv = subset_check(subset={"nope"}, set_={"hello", "world"})
    assert rv == False, "Return value should be False."
    assert isinstance(rv, bool), "Return value should be bool."
