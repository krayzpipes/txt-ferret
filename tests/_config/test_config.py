import copy

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
def default_config():
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


# Test _add_user_config_file function


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


def test_add_user_config_file_no_user_config(default_config, validator_true):
    config_copy = copy.deepcopy(default_config)
    rv = _add_user_config_file(
        config_=config_copy,
        yaml_file=None,
        default_override=False,
        _user_config={"fake_key", "fake_value"},
        validator=validator_true,
    )
    assert default_config == rv, "Dicts should be the same."


def test_add_user_config_file_default_override_with_user_config(
    default_config, user_config, validator_true
):
    config_copy = copy.deepcopy(default_config)
    expected_config = copy.deepcopy(default_config)
    expected_config["filters"] = copy.deepcopy(user_config["filters"])
    rv = _add_user_config_file(
        config_=config_copy,
        yaml_file=None,
        default_override=True,
        _user_config=user_config,
        validator=validator_true,
    )
    assert (
        expected_config["filters"] == rv["filters"]
    ), "Expected default filters to be replaced by user-defined filters."
    assert expected_config == rv, "Only the filters should have been changed."


def test_add_user_config_file_no_default_override_with_user_config(
    default_config, user_config, validator_true
):
    config_copy = copy.deepcopy(default_config)
    expected_config = copy.deepcopy(default_config)
    user_filters = copy.deepcopy(user_config["filters"])
    expected_config["filters"] += user_filters
    rv = _add_user_config_file(
        config_=config_copy,
        yaml_file=None,
        default_override=False,
        _user_config=user_config,
        validator=validator_true,
    )
    assert (
        expected_config["filters"] == rv["filters"]
    ), "Expected both default and user filters in the final dict."
    assert expected_config == rv, "Only the filters should have been changed."


def test_add_user_config_file_change_settings(validator_true):
    original_config = {"settings": {"key_1": "original_value_1"}}
    user_config= {"settings": {"key_1": "user_value_1"}}
    rv = _add_user_config_file(
        config_=original_config,
        yaml_file=None,
        default_override=False,
        _user_config=user_config,
        validator=validator_true,
    )
    assert original_config == user_config, "Expected user settings to override default."


def test_add_user_config_file_validation_failed(validator_raise):
    with pytest.raises(ValueError):
        _ = _add_user_config_file(
            config_={"key": "value"},
            yaml_file=None,
            default_override=False,
            _user_config={"who": "cares"},
            validator=validator_raise,
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