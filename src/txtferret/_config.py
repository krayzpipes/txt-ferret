import os

import yaml

from ._default import default_yaml


# Keys allowed in top lovel of config.
_allowed_top_level = {"filters", "settings"}

# Keys allowed for a filter in the config YAML file.
_allowed_filter_keys = {"label", "type", "pattern", "tokenize", "sanity"}

# Keys allowed for the filter.tokenize values.
_allowed_token_keys = {"mask", "index"}

# Keys required for a filter to pass validation.
_required_filter_keys = {"label", "pattern"}

# Keys allowed for settings section in the config YAML file.
_allowed_settings_keys = {
    "tokenize",
    "log_level",
    "summarize",
    "output_file",
    "show_matches",
    "delimiter",
    "ignore_columns",
}


def _load_config(yaml_file=None):
    """Return a dict containing config YAML file content.

    :return: dict containing config YAML file content.
    """
    with open(yaml_file, "r") as f:
        return yaml.safe_load(f)


def _load_default_config(config_string=None):
    """Return a dict containing default config YAML content.

    :return: dict containing default config YAML file content.
    """
    default_yaml_config = config_string or default_yaml
    return yaml.safe_load(default_yaml_config)


def load_config(yaml_file=None, config_=None, user_config_func=None):
    """Return dict containing config YAML file content.

    If not YAML file is explicitly passed as an argument, this function
    will load and then return the contents from the default YAML
    config file.

    :param yaml_file: YAMl file name containing config information.
    :param config_: Used for tests.

    :return: dict with the final configuration.
    """
    # Load the default config as the final config, we will make
    # adjustments as we look at the user-defined config.

    if yaml_file is None:
        default_config = config_ or _load_default_config()
        return default_config

    _user_config_load = user_config_func or _get_user_config_file

    return _user_config_load(yaml_file=yaml_file)


def _get_user_config_file(yaml_file=None, _user_config=None, validator=None):
    """Return dict containing default config + user defined config.

    :param yaml_file: File name of user-defined configuration.
    :param _user_config: Configuration used for tests.
    :param validator: Used to pass in validation stubs during tests.

    :return: dict containing the user-defined configuration file.
    """
    user_defined_config = _user_config or _load_config(yaml_file)

    _validator = validator or validate_config

    _validator(user_defined_config)

    return user_defined_config


def save_config(data, file_name):
    """Write default config to file of user's choice for future ref."""
    with open(file_name, "w+") as wf:
        yaml.dump(data, wf, default_flow_style=False)


def subset_check(subset=None, set_=None):
    """Return True/False depending on if set is subset of larger set.

    If subset - set_ != 0, then subset contains keys that are not in
    set_.

    set_ is our 'allowed keys' in this use case.

    Another use case is testing if a required subset exists in set_.
    For example, looking for keys that are REQUIRED to be in the config.

    :param subset: The set we are checking to see if it is a subset of
        set_.
    :param set_: The set_ being tested against.

    :return: True if subset, False if it isn't.
    """
    if subset - set_:
        return False
    return True


def validate_config(
    config_dict,
    top_level=None,
    filter_keys=None,
    required_keys=None,
    token_keys=None,
    settings_keys=None,
):
    """Raise error if configuration is not valid.

    !! This bad boy could use some major refactoring. !!

    :param config_dict: The configuration to validate.
    :param top_level: Allowed top level keys. For testing purposes.
    :param filter_keys: Allowed filter keys. For testing purposes.
    :param required_keys: Required filter keys. For testing purposes.
    :param token_keys: Allowed tokenize keys. For testing purposes.

    :raises: ValueError - Bad configuration + details.
    """
    # Make sure only allowed values at top level of config.
    top_level_keys = set(config_dict.keys())
    allowed_top_level = top_level or _allowed_top_level

    if not subset_check(subset=top_level_keys, set_=allowed_top_level):
        raise ValueError("Bad config: One or more top-lvel keys are not allowed.")

    # Validate the filters portion of the config.
    if "filters" in config_dict:
        for filter_ in config_dict["filters"]:

            _filter_keys = set(filter_.keys())
            allowed_filter_keys = filter_keys or _allowed_filter_keys

            if not subset_check(subset=_filter_keys, set_=allowed_filter_keys):
                raise ValueError("Bad config: One or more filter keys are not allowed.")

            # Note, the set order is switched up here as we want to find
            # which keys in the subset (required) are NOT in the main
            # set (The actual keys).
            required_filter_keys = required_keys or _required_filter_keys

            if not subset_check(subset=required_filter_keys, set_=_filter_keys):
                raise ValueError(
                    "Bad config: One or more filters does not have required keys."
                )

            if filter_.get("tokenize", None) is not None:

                _token_keys = set(filter_["tokenize"].keys())
                allowed_token_keys = token_keys or _allowed_token_keys

                if not subset_check(subset=_token_keys, set_=allowed_token_keys):
                    raise ValueError(
                        "Bad config: One or more filter token keys is not allowed."
                    )

    # Validate the settings portion of the config.
    if "settings" in config_dict:

        _settings_keys = set(config_dict["settings"].keys())
        allowed_settings_keys = settings_keys or _allowed_settings_keys

        if not subset_check(subset=_settings_keys, set_=allowed_settings_keys):
            raise ValueError("Bad config: One or more settings are not allowed.")
