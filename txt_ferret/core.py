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

def _byte_code_to_string(byte_code):
    match = re.match("b(\d{1,3})", byte_code)
    if not match:
        return byte_code
    code_ = int(match.group(1))
    return bytes((code_,)).decode('utf-8')

class Filter:
    def __init__(self, filter_dict):
        self.label = filter_dict.get("label", "NOT_DEFINED")

        try:
            self.pattern = filter_dict["pattern"]
        except KeyError:
            raise ValueError("Pattern missing from filter.")

        self.type = filter_dict.get("type", "NOT_DEFINED")
        self.sanity = filter_dict.get("sanity", "")

        if isinstance(self.sanity, str):
            self.sanity = [self.sanity]

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
    def __init__(self, file_name=None, config_file=None, config_=None, **cli_settings):
        config = config_ or load_config(yaml_file=config_file)
        self.file_name = file_name

        # Set settings from file.
        self.set_attributes(**config["settings"])

        # Override settings from file with CLI arguments if present.
        self.set_attributes(**cli_settings)

        self.failed_sanity = 0
        self.passed_sanity = 0

        self.filters = [
            Filter(filter_dict=filter_) for filter_ in config["filters"]
        ]

    def set_attributes(self, **kwargs):
        for setting, value in kwargs.items():

            if setting not in _allowed_settings_keys:
                continue

            if not value:
                continue

            if setting == "no_tokenize":
                self.tokenize = False
                continue

            setattr(self, setting, value)

    def _get_file_size(self):
        file_ = Path(self.file_name)
        mb = file_.stat().st_size / 1024 / 1024
        return mb



    def scan_file(self, file_name=None):
        start = datetime.now()

        file_to_scan = file_name

        with open(file_to_scan, "r") as rf:
            for index, line in enumerate(rf):
                if self.delimiter:
                    self._scan_delimited_line(line, index)
                    continue
                self._scan_non_delimited_line(line, index)

        end = datetime.now()
        delta = end - start

        logger.info(f"Regex matched but failed sanity check: {failed_sanity}")
        logger.info(f"Regex matched and passed sanity check: {passed_sanity}")

        seconds = delta.seconds
        minutes = delta.seconds // 60

        logger.info(f"Finished in {seconds} seconds ({minutes} minutes).")


    def _scan_delimited_line(self, line, index):
        for filter_ in self.filters:
            column_map = {}
            delimiter = _byte_code_to_string(self.delimiter)

            columns = line.split(delimiter)

            # Look for matches in each column.
            for i, column in enumerate(columns):
                matches = filter_.regex.findall(column)

                if not matches:
                    continue

                for match in matches:
                    if str(i) not in columns:
                        columns[str(i)] = []

                    columns[str(i)].append(match)

            for column_number, column_match_list in column_map.items():
                for column_match in column_match_list:

                    if not test_sanity(filter_, column_match):
                        self.failed_sanity += 1

                        if not self.summarize:
                            log_failure(filter_, index)

                        continue

                    self.passed_sanity += 1

                    string_to_log = tokenize(
                        column_match, filter_.token_mask,
                        filter_.token_index, tokenize=self.tokenize,
                        show_matches=self.show_matches,
                    )

                    if not self.summarize:
                        log_success(
                            filter_, index, string_to_log, column=int(column_number)
                        )


    def _scan_non_delimited_line(self, line=None, index=None):
        for filter_ in self.filters:
            matches = filter_.regex.findall(line)

            if not matches:
                return 0, 0

            for match in matches:
                if not test_sanity(filter_, match):
                    self.failed_sanity += 1
                    if not self.summarize:
                        log_failure(filter_, index)
                    continue

                self.passed_sanity += 1

                string_to_log = tokenize(
                    match, filter_.token_mask,
                    filter_.token_index, tokenize=self.tokenize,
                    show_matches=self.show_matches,
                )

                if not self.summarize:
                    log_success(filter_, index, string_to_log)


def test_sanity(self, filter_, text):

    for algorithm_name in filter_.sanity:
        if not sanity_check(algorithm_name, text):
            return False
    return True


def log_success(self, filter_, index, string_, column=None):
    matched_string = string_
    if column:
        message = (
            f"Matched and passed sanity - Filter: {filter_.label}, "
            f"Line {index + 1}, String: {matched_string}, Column: {column}"
        )
    else:
        message = (
            f"Matched and passed sanity - Filter: {filter_.label}, "
            f"Line {index + 1}, String: {matched_string}"
        )
    logger.info(message)


def log_failure(self, filter_, index, column=None, config=None):
    if column:
        message = (
            f"Matched and FAILED sanity - Filter: {filter_.label}, "
            f"Line: {index + 1}, Column: {column + 1}"
        )
    else:
        message = (
            f"Matched and FAILED sanity - Filter: {filter_.label}, "
            f"Line: {index + 1}"
        )
    logger.debug(message)
