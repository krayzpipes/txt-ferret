import os

import yaml

from ._default import default_yaml


# Keys allowed in top lovel of config.
_allowed_top_level = {"filters", "settings"}

# Keys allowed for a filter in the config YAML file.
_allowed_filter_keys = {"label", "type", "pattern", "tokenize", "sanity"}

# Keys allowed for the filter.tokenize values.
_allowed_tokenize_keys = {"mask", "index"}

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
}


def _load_config(yaml_file=None):
    """Return a dict containing config YAML file content.

    :return: dict containing config YAML file content.
    """
    with open(yaml_file, "r") as f:
        return yaml.safe_load(f)


def _load_default_config(yaml_file=None):
    """Return a dict containing default config YAML content.

    :return: dict containing default config YAML file content.
    """
    if yaml_file is not None:
        with open(yaml_file, "r") as f:
            return yaml.safe_load(f)
    return yaml.safe_load(default_yaml)



def load_config(yaml_file=None, default_override=False):
    """Return dict containing config YAML file content.

    If not YAML file is explicitly passed as an argument, this function
    will load and then return the contents from the default YAML
    config file.

    :param yaml_file: YAMl file name containing config information.
    :param default_override: If set to 'True', this will result in
        the final returned config dict containing only user-defined
        filters. The defaults will be completely overridden.

    :return: dict with the final configuration.
    """
    # Load the default config as the final config, we will make
    # adjustments as we look at the user-defined config.
    working_config = _load_default_config()

    # Return default config if no file is defined by user or settings
    # introduced through CLI switches.
    if yaml_file is None:
        return working_config

    # Mix in the user config if present and return it.
    # If default_override is True, we should return filters ONLY
    # defined by the user.
    return _add_user_config_file(working_config, yaml_file, default_override)


def _add_user_config_file(config_, yaml_file, default_override):
    """Return dict containing default config + user defined config.

    If default_override is set to 'True', then only return the
    user-defined filters.

    :param config_: dict containing config file content.
    :param yaml_file: File name of user-defined configuration.
    :param default_override: If set to True, will only return filters
        defined by the user. Default filters will not be returned.

    :return: dict containing the default + user + cli-defined
        configuration.
    """
    user_defined_config = _load_config(yaml_file)
    validate_config(user_defined_config)

    if "filters" in user_defined_config:
        if default_override:
            # Remove default filters completely.
            config_["filters"] = user_defined_config["filters"]
        else:
            # Add user filters to default filters.
            for filter_ in user_defined_config["filters"]:
                config_["filters"].append(filter_)

    if "settings" in user_defined_config:
        for key, value in user_defined_config["settings"].items():
            config_["settings"][key] = value

    return config_


def save_config(data, file_name):
    """Write default config to file of user's choice for future ref."""
    with open(file_name, "w+") as wf:
        yaml.dump(data, wf, default_flow_style=False)


def _top_level_keys_allowed(key_list, allowed=None):
    """Return True if given keys are all allowed keys for top level."""
    top_level_allowed = allowed or _allowed_top_level
    if set(key_list) - top_level_allowed:
        return False
    return True


def _filter_keys_allowed(key_list, allowed=None):
    """Return True if given keys are all allowed keys for filters."""
    filter_keys_allowed = allowed or _allowed_filter_keys
    if set(key_list) - filter_keys_allowed:
        return False
    return True


def _filter_tokenize_keys_allowed(key_list, allowed=None):
    """Return True if filter.tokenize keys are all allowed."""
    filter_tokenize_keys_allowed = allowed or _allowed_tokenize_keys
    if set(key_list) - filter_tokenize_keys_allowed:
        return False
    return True


def _filter_have_required_keys(key_list, required=None):
    """Return True if given keys contain all required keys."""
    required_ = required or _required_filter_keys
    if required_ - set(key_list):
        return False
    return True


def _filter_settings_keys_allowed(key_list, allowed=None):
    """Return True if all keys are allowed settings keys."""
    settings_keys_allowed = allowed or _allowed_settings_keys
    if set(key_list) - settings_keys_allowed:
        return False
    return True


def validate_config(config_dict):
    """Raise error if configuration is not valid."""

    # Make sure only allowed values at top level of config.
    if not _top_level_keys_allowed(config_dict.keys()):
        raise ValueError("Bad config: One or more top-lvel keys are not allowed.")

    # Validate the filters portion of the config.
    if "filters" in config_dict:
        for filter_ in config_dict["filters"]:

            if not _filter_keys_allowed(filter_.keys()):
                raise ValueError("Bad config: One or more filter keys are not allowed.")

            if not _filter_have_required_keys(filter_.keys()):
                raise ValueError(
                    "Bad config: One or more filters does not have required keys."
                )

            if filter_.get("tokenize", None) is not None:
                if not _filter_tokenize_keys_allowed(filter_["tokenize"].keys()):
                    raise ValueError(
                        "Bad config: One or more filter token keys is not allowed."
                    )

    # Validate the settings portion of the config.
    if "settings" in config_dict:
        if not _filter_settings_keys_allowed(config_dict["settings"].keys()):
            raise ValueError("Bad config: One or more settings are not allowed.")
