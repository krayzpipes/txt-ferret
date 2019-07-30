import copy

import pytest

from txtferret._config import (
    _load_config,
    _load_default_config,
    load_config,
    _get_user_config_file,
    save_config,
    subset_check,
    validate_config,
)


# Test _load_default_config function


def test_load_default_config():
    config_string = """
    settings:
      setting1: value1
      setting2: value2
    """
    config_dict = {"settings": {"setting1": "value1", "setting2": "value2"}}
    assert _load_default_config(config_string=config_string) == config_dict


# TODO: test_load_default_config for actual yaml file load.

# TODO: test _load_config


def test_load_config_no_custom_config():
    def stub_func(yaml_file=None):
        return {"dont": "return_me"}

    rv = load_config(
        yaml_file=None, config_={"mytest": "config"}, user_config_func=stub_func
    )

    assert {"mytest": "config"} == rv, "dict should be the same"


def test_load_config_return_custom_config():
    def stub_func(yaml_file=None):
        return {"my": "config"}

    jv = load_config(
        yaml_file="something", config_={"dont": "return_me"}, user_config_func=stub_func
    )

    assert {"my": "config"} == jv, "returned the wrong dict"


@pytest.fixture(scope="module")
def user_config():
    config = {
        "filters": [
            {
                "label": "user_config_filter_1",
                "type": "user_config_filter_type_1",
                "sanity": "user_config_filter_sanity_1",
                "pattern": "(user_config_filter_regex_1)",
                "tokenize": {"mask": "user_config_mask_1", "index": "1"},
            }
        ],
        "settings": {
            "tokenize": True,
            "log_level": "INFO",
            "summarize": False,
            "output_file": None,
            "show_matches": True,
            "delimiter": None,
        },
    }
    return config


@pytest.fixture(scope="module")
def custom_config():
    config = {
        "filters": [
            {
                "label": "default_config_filter_1",
                "type": "default_config_filter_type_1",
                "sanity": "default_config_filter_sanity_1",
                "pattern": "(default_config_filter_regex_1)",
                "tokenize": {"mask": "default_config_mask_1", "index": "2"},
            }
        ],
        "settings": {
            "tokenize": True,
            "log_level": "INFO",
            "summarize": False,
            "output_file": None,
            "show_matches": True,
            "delimiter": None,
        },
    }
    return config


# Test _get_user_config_file function


@pytest.fixture(scope="module")
def validator_true():
    def validator_func(not_used):
        return True

    return validator_func


@pytest.fixture(scope="module")
def validator_raise():
    def validator_func(not_used):
        raise ValueError("This is a test.")

    return validator_func


def test_get_user_config_file_valid(validator_true):
    rv = _get_user_config_file(
        yaml_file=None,
        _user_config={"fake_key": "fake_value"},
        validator=validator_true,
    )
    assert {"fake_key": "fake_value"} == rv, "Dicts should be the same."


def test_get_user_config_file_validation_failed(validator_raise):
    with pytest.raises(ValueError):
        _ = _get_user_config_file(
            yaml_file=None, _user_config={"who": "cares"}, validator=validator_raise
        )


# Testing the subset_check function


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


# Test validate_config function

# TODO: continue writing tests.
