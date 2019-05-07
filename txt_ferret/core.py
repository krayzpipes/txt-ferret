from datetime import datetime
from pathlib import Path
import re

from loguru import logger

from ._config import load_config, _allowed_settings_keys
from ._sanity import sanity_check


def tokenize(clear_text, mask, index, tokenize=True, show_matches=False):
    if not show_matches:
        return "REDACTED"
    if not tokenize:
        return clear_text
    return _get_tokenized_string(clear_text, mask, index)


def _get_tokenized_string(text, mask, index):
    end_index = index + len(mask)
    text_length = len(text)
    if (text_length - 1) < end_index:
        temp_string = f"{text[:index]}{mask}"
        return temp_string[:text_length]
    return f"{text[:index]}{mask}{text[end_index:]}"


class Filter:
    def __init__(self, filter_dict):
        self.label = filter_dict.get("label", "NOT_DEFINED")

        try:
            self.pattern = filter_dict["pattern"]
        except KeyError:
            raise ValueError("Pattern missing from filter.")

        self.type = filter_dict.get("type", "NOT_DEFINED")
        self.sanity = filter_dict.get("sanity", "")

        try:
            self.token_mask = filter_dict["tokenize"].get("mask", "XXXXXXXXXXXXXXX")
        except KeyError:
            self.token_mask = "XXXXXXXXXXXXXXX" # move this to the default
            self.token_index = 0
            logger.info(
                f"Filter {self.label} did not have tokenize section. Reverting to "
                f"default tokenization mask and index."
            )

        try:
            self.token_index = int(filter_dict["tokenize"].get("index", 0))
        except ValueError:
            raise ValueError(f"Token index for {self.label} filter is not an integer.")

        self.regex = re.compile(self.pattern)


class TxtFerret:
    def __init__(self, file_name=None, config_file=None, config_=None, **kwargs):
        self.file_name = file_name
        self.config = config_ or load_config(yaml_file=config_file)

        # Note that settings from the CLI will overwrite settings from
        # user defined config and default config.

        for setting, value in kwargs.items():

            if not value:
                continue

            if setting == "no_tokenize":
                self.config["settings"]["tokenize"] = False
                continue

            if setting not in _allowed_settings_keys:
                continue

            self.config["settings"][setting] = value

        self.filters = [
            Filter(filter_dict=filter_) for filter_ in self.config["filters"]
        ]

    def _get_file_size(self):
        file_ = Path(self.file_name)
        mb = file_.stat().st_size / 1024 / 1024
        return mb

    def scan_file(self, file_name=None):
        start = datetime.now()
        failed_sanity = 0
        passed_sanity = 0

        file_to_scan = file_name or self.file_name

        with open(file_to_scan, "r") as rf:
            for index, line in enumerate(rf):
                failed, passed = self.scan_line(index, line)
                failed_sanity += failed
                passed_sanity += passed

        end = datetime.now()
        delta = end - start

        logger.info(f"Regex matched but failed sanity check: {failed_sanity}")
        logger.info(f"Regex matched and passed sanity check: {passed_sanity}")

        seconds = delta.seconds
        minutes = delta.seconds // 60

        logger.info(f"Finished in {seconds} seconds ({minutes} minutes).")


    def scan_line(self, index, line):
        _failed_sanity = 0
        _passed_sanity = 0
        redact_setting = self.config["settings"]["show_matches"]
        tokenize_setting = self.config["settings"]["tokenize"]

        for filter_ in self.filters:
            summarize_setting = self.config["settings"]["summarize"]
            matches = filter_.regex.findall(line)

            if not matches:
                continue

            filtered_list = [re.sub("[\W_]", "", match) for match in matches]

            if isinstance(filter_.sanity, str):
                filter_.sanity = [filter_.sanity]

            for filtered_string in filtered_list:
                if not self.test_sanity(filter_, filtered_string):
                    _failed_sanity += 1
                    if not summarize_setting:
                        self.log_failure(filter_, index)
                    continue


                final_string = tokenize(
                    filtered_string, filter_.token_mask,
                    filter_.token_index, tokenize=tokenize_setting,
                    show_matches=redact_setting,
                )

                _passed_sanity += 1
                if not summarize_setting:
                    self.log_success(filter_, index, final_string)

        return _failed_sanity, _passed_sanity

    def test_sanity(self, filter_, text):
        if isinstance(filter_.sanity, str):
            filter_.sanity = [filter_.sanity]

        for algorithm_name in filter_.sanity:
            if not sanity_check(algorithm_name, text):
                return False
        return True

    def log_success(self, filter_, index, string_):
        matched_string = string_
        message = (
            f"Matched and passed sanity - Filter: {filter_.label}, "
            f"Line {index + 1}, String: {matched_string}"
        )
        logger.info(message)

    def log_failure(self, filter_, index, config=None):
        message = (
            f"Matched and FAILED sanity - Filter: {filter_.label}, "
            f"Line: {index + 1}"
        )
        logger.debug(message)
