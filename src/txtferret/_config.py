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


def validate_config(config_dict):
    """Raise error if configuration is not valid."""

    # Make sure only allowed values at top level of config.
    top_level_keys = set(config_dict.keys())

    if not subset_check(subset=top_level_keys, set_=_allowed_top_level):
        raise ValueError("Bad config: One or more top-lvel keys are not allowed.")

    # Validate the filters portion of the config.
    if "filters" in config_dict:
        for filter_ in config_dict["filters"]:

            filter_keys = set(filter_.keys())

            if not subset_check(subset=filter_keys, set_=_allowed_filter_keys):
                raise ValueError("Bad config: One or more filter keys are not allowed.")

            # Note, the set order is switched up here as we want to find
            # which keys in the subset (required) are NOT in the main
            # set (The actual keys).
            if not subset_check(subset=_required_filter_keys, set_=filter_keys):
                raise ValueError(
                    "Bad config: One or more filters does not have required keys."
                )

            if filter_.get("tokenize", None) is not None:

                token_keys = set(filter_["tokenize"].keys())

                if not subset_check(subset=token_keys, set_=_allowed_token_keys):
                    raise ValueError(
                        "Bad config: One or more filter token keys is not allowed."
                    )

    # Validate the settings portion of the config.
    if "settings" in config_dict:

        settings_keys = set(config_dict["settings"].keys())

        if not subset_check(subset=settings_keys, set_=_allowed_settings_keys):
            raise ValueError("Bad config: One or more settings are not allowed.")
