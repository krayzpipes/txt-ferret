
import os
from pathlib import Path
import re

from loguru import logger
import yaml

from ._config import load_config, validate_config
from ._sanity import sanity_mapping


class Filter:
    def __init__(self, filter_dict):
        self.label = filter_dict.get("label", "NOT_DEFINED")

        try:
            self.pattern = filter_dict["pattern"]
        except KeyError
            raise ValueError("Pattern missing from filter.")

        self.type = filter_dict.get("type", "NOT_DEFINED")
        self.sanity = filter_dict.get("sanity", "")

        try:
            self.token_mask = filter_dict["tokenize"].get("mask", "XXXXXXXXXXXXXXX")
        except KeyError:
            self.token_mask = "XXXXXXXXXXXXXXX"
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
        failed_luhn = 0
        passed_luhn = 0
        file_to_scan = file_name or self.file_name
        with open(file_to_scan, "r") as rf:
            for index, line in enumerate(rf):
                failed, passed = self.scan_line(index, line)
                failed_luhn += failed
                passed_luhn += passed
        logger.info(f"Regex matched  but luhn failed summary: {failed_luhn}")
        logger.info(f"Regex matched and luhn passed summary: {passed_luhn}")


    def scan_line(self, index, line):
        _failed_luhn = 0
        _passed_luhn = 0
        for key, regex in self._ccn_regex_compiled.items():
            match = regex.search(line)

            if not match:
                continue

            filtered = re.sub("[\W_]", "", match.group(1))
            luhn_result = luhn(filtered)

            if not luhn_result:
                _failed_luhn += 1
                if not self.config.SUMMARIZE:
                    logger.debug(
                        f"{key} regex matched but luhn tested negative: line {index}."
                    )
                continue
            result_string = self.tokenize(filtered)
            _passed_luhn += 1
            if not self.config.SUMMARIZE:
                logger.info(
                    f"Regex for {key} matched an passed Luhn test on line "
                    f"{index+1}: {result_string}"
                )
        return _failed_luhn, _passed_luhn

    def tokenize(self, clear_text):
        if not self._tokenize_flag:
            return clear_text
        tokenized_text = f"{clear_text[0:4]}{self._tokenize_string}{clear_text[12:]}"
        return tokenized_text
