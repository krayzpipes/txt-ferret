import os

import yaml


current_dir = os.path.abspath(os.path.dirname(__file__))

_allowed_top_level = {"filters", "settings"}
_allowed_filter_keys = {
    "label",
    "type",
    "pattern",
    "tokenize",
    "sanity",
}
_allowed_tokenize_keys = {"mask", "index"}
_required_filter_keys = {"label", "pattern"}
_allowed_settings_keys = {
    "tokenize",
    "log_level",
    "summarize",
}

def _load_config(yaml_file=None):
    with open(yaml_file, "r") as f:
        return yaml.safe_load(f)


def _load_default_config(yaml_file="_default.yaml"):
    if yaml_file == "_default.yaml":
        yaml_file = os.path.join(current_dir, yaml_file)
    with open(yaml_file, "r") as f:
        return yaml.safe_load(f)


def load_config(yaml_file=None, include_default=True):

    # Load the default config as the final config, we will make
    # asjustements as we look at the user-defined config.
    final_config = _load_default_config()
    if yaml_file is None:
        return final_config

    user_defined_config = _load_config(yaml_file)

    validate_config(user_defined_config)

    # If the user config has filters, add them to the final config.
    # If the user chose to exclude default filters, then don't use
    # them.
    if "filters" in user_defined_config:
        if not include_default:
            final_config["filters"] = user_defined_config["filters"]
        else:
            for filter_ in user_defined_config["filters"]:
                final_config["filters"].append(filter_)

    if "settings" in user_defined_config:
        for key, value in user_defined_config["settings"].items():
            final_config["settings"][key] = value

    return final_config


def save_config(data, file_name):
    with open(file_name, "w+") as wf:
        yaml.dump(data, wf, default_flow_style=False)

def _top_level_keys_allowed(key_list, allowed=None):
    top_level_allowed = allowed or {"filters", "settings"}
    if set(key_list) - top_level_allowed:
        return False
    return True


def _filter_keys_allowed(key_list, allowed=None):
    filter_keys_allowed = allowed or {"label", "type", "pattern", "tokenize"}
    if set(key_list) - filter_keys_allowed:
        return False
    return True


def _filter_tokenize_keys_allowed(key_list, allowed=None):
    filter_tokenize_keys_allowed = allowed or {"mask", "index"}
    if set(key_list) - filter_tokenize_keys_allowed:
        return False
    return True


def _filter_have_required_keys(key_list, required=None):
    required_ = required or {"label", "pattern"}
    if required_ - set(key_list):
        return False
    return True

def _filter_settings_keys_allowed(key_list, allowed=None):
    settings_keys_allowed = allowed or _allowed_settings_keys
    if set(key_list) - settings_keys_allowed:
        return False
    return True

def validate_config(config_dict):
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