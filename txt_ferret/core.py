
import os
from pathlib import Path
import re

from loguru import logger

from ._config import load_config, validate_config
from ._sanity import sanity_check


def tokenize(clear_text, mask, index, tokenize=True):
    if not tokenize:
        return clear_text
    return _get_tokenized_string()


def _get_tokenized_string(text, mask, index):
    end_index = index + len(mask)
    text_length =len(text)
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
        else:
            self.token_index = filter_dict["tokenize"].get("index", 0)

        self.regex = re.compile(self.pattern)


class TxtFerret:
    def __init__(
            self, file_name=None, ccn_mapping=None, tokenize=True,
            config_file=None, config_=None, settings=None,
    ):
        self.file_name = file_name
        self.config = config_ or load_config(yaml_file=config_file)
        if settings is not None:
            validate_config(settings)
            for key, value in settings:
                self.config["settings"][key] = value
        self.filters = [
            Filter(filter_dict=filter_) for filter_ in self.config["filters"]
        ]

    def _get_file_size(self):
        file_ = Path(self.file_name)
        mb = file_.stat().st_size / 1024 / 1024
        return mb

    def scan_file(self, file_name=None):
        failed_sanity = 0
        passed_sanity = 0
        file_to_scan = file_name or self.file_name
        with open(file_to_scan, "r") as rf:
            for index, line in enumerate(rf):
                failed, passed = self.scan_line(index, line)
                failed_sanity += failed
                passed_sanity += passed
        logger.info(f"Regex matched but failed sanity check: {failed_sanity}")
        logger.info(f"Regex matched and passed sanity check: {passed_sanity}")


    def scan_line(self, index, line):
        _failed_sanity = 0
        _passed_sanity = 0

        for filter_ in self.filters:
            match = filter_.regex.search(line)

            if not match:
                continue

            filtered = re.sub("[\W_]", "", match.group(1))

            if isinstance(filter_.sanity, str):
                filter_.sanity = [filter_.sanity]

            failed_sanity_flag = False
            for algorithm_name in filter_.sanity:
                if not sanity_check(algorithm_name, filtered):
                    failed_sanity_flag = True


            if failed_sanity_flag:
                _failed_sanity += 1
                if not self.config["summarize"]:
                    logger.debug(
                        f"{filter_.label} regex matched but sanity check "
                        f"failed: line {index}."
                    )
                continue

            final_string = tokenize(filter)
            _passed_sanity += 1
            if not self.config["summarize"]:
                logger.info(
                    f"{filter_.label} matched on line {index+1} and "
                    f"passed sanity check: {final_string}"
                )
        return _failed_sanity, _passed_sanity

