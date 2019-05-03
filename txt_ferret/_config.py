
import yaml

def _load_config(yaml_file=None):
    with open(yaml_file, "r") as f:
        return yaml.safe_load(f)


def _load_default_config(yaml_file="_default.yaml"):
    with open(yaml_file, "r") as f:
        return yaml.safe_load(f)


def load_config(yaml_file=None, include_default=True):
    final_config = _load_default_config()
    if yaml_file is None:
        return final_config
    user_defined_config = _load_config(yaml_file)

    validate_config(user_defined_config)

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


def validate_config(config_dict):
    if not _top_level_keys_allowed(config_dict.keys()):
        raise ValueError("Bad config: One or more top-lvel keys are not allowed.")

    if config_dict.get("filters", None) is not None:
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

    # TODO - settings validations
