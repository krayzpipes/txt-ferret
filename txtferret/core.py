"""Core classes and functions for txt_ferret."""

from datetime import datetime
from pathlib import Path
import re

from loguru import logger

from ._config import load_config, _allowed_settings_keys
from ._sanity import sanity_check


def tokenize(clear_text, mask, index, tokenize=True, show_matches=False):
    """Return string as redacted, tokenized format, or clear text.

    :param clear_text: The text to be tokenized.
    :param mask: The mask to be applied to the clear text.
    :param index: Which index in the clear_text string the mask should
        start at.
    :param tokenize: Bool representing whether the clear text should be
        tokenized or not.
    :param show_matches: Bool representing whether the clear text should
        be redacted all together or not.
    """
    if not show_matches:
        return "REDACTED"
    if not tokenize:
        return clear_text
    return _get_tokenized_string(clear_text, mask, index)


def _get_tokenized_string(text, mask, index):
    """Return tokenized string.

    :Note: If the mask length will cause the final string to be longer
        than the original string, then the mask will be cut down to
        size.
    """
    end_index = index + len(mask)
    text_length = len(text)
    if (text_length - 1) < end_index:
        temp_string = f"{text[:index]}{mask}"
        return temp_string[:text_length]
    return f"{text[:index]}{mask}{text[end_index:]}"


def _byte_code_to_string(byte_code):
    """Return the UTF-8 form of a byte code.

    :param byte_code: String that may contain a string that matches the
        bytcode format defined by txt-ferret. (Ex: Start of Header would
        be passed into this function as 'b01' instead of '\x01' as
        there are issues passing backslashes through the CLI arguments.

    :return: UTF-8 version of byte-code.
    """
    match = re.match("b(\d{1,3})", byte_code)
    if not match:
        return byte_code
    code_ = int(match.group(1))
    return bytes((code_,)).decode("utf-8")


class Filter:
    """ Helper class to  hold filter configurations and add a simple
    API to interface with Filter attributes.

    :attribute label: The name of the filter in question.
    :attribute pattern: The regular expression that will be used to
        match text.
    :attribute type: A classification of the filter.
    :attribute sanity: The name of the sanity check (ex: 'luhn').
    :attribute token_mask: Mask used to mask filter results.
    :attribute token_index: Index in clear-text string in which the
        mask should start being applied.
    """

    def __init__(self, filter_dict):
        """Initialize the Filter object. Lots handling input from
        the config file here.

        :raise: ValueError - Pattern missing from filter.
        :raise: ValueError - Token index is not an integer.
        """
        self.label = filter_dict.get("label", "NOT_DEFINED")

        # Get pattern from filter. This is required, so raise an
        # exception if it's missing.
        try:
            self.pattern = filter_dict["pattern"]
        except KeyError:
            raise ValueError("Pattern missing from filter.")

        self.type = filter_dict.get("type", "NOT_DEFINED")
        self.sanity = filter_dict.get("sanity", "")

        # Sanity should be a list of strings. If just a string, convert
        # it to a list with a single element.
        if isinstance(self.sanity, str):
            self.sanity = [self.sanity]

        try:
            self.token_mask = filter_dict["tokenize"].get("mask", "XXXXXXXXXXXXXXX")
        except KeyError:
            self.token_mask = "XXXXXXXXXXXXXXX"  # move this to the default
            self.token_index = 0
            logger.info(
                f"Filter did not have tokenize section. Reverting to "
                f"default tokenization mask and index."
            )

        try:
            self.token_index = int(filter_dict["tokenize"].get("index", 0))
        except ValueError:
            raise ValueError(f"Token index for filter is not an integer.")

        self.regex = re.compile(self.pattern)


class TxtFerret:
    """Class to hold state and manage scanning files for data.

    Some attributes are dynamically assigned based on contents of the
    config/settings file or CLI arguments/switches.

    :attribute file_name: The name of the file to scan.
    :attribute tokenize: Determines if txt_ferret will tokenize the
        output of strings that match and pass sanity checks.
    :attribute log_level: Log level to be used by logouru.logger.
    :attribute summarize: If True, only outputs summary of the scan
        resutls.
    :attribute output_file: File to write results to.
    :attribute show_matches: Show or redact matched strings.
    :attribute delimiter: String representing the delimiter for
        columns within the file. If present, txt_ferret will scan
        each column and also report column number in output.
    :attribute failed_sanity: Count of strings that matched a filter
        but failed sanity checks.
    :attribute passed_sanity: Count of strings that matched a filter
        and passed sanity checks.
    :attribute filters: List of filters to be used during the file scan.
    """

    def __init__(self, file_name=None, config_file=None, config_=None, **cli_settings):
        """Initialize the TxtFerret object."""
        config = config_ or load_config(yaml_file=config_file)
        self.file_name = file_name

        # Set settings from file.
        self.set_attributes(**config["settings"])

        # Override settings from file with CLI arguments if present.
        self.set_attributes(**cli_settings)

        # Counters
        self.failed_sanity = 0
        self.passed_sanity = 0

        self.filters = [Filter(filter_dict=filter_) for filter_ in config["filters"]]

    def set_attributes(self, **kwargs):
        """Sets attributes for the TxtFerret object.

        These attributes are based on the YAML config files as well
        as the CLI arguments."""
        for setting, value in kwargs.items():

            if setting == "no_tokenize":
                if not value:
                    continue
                self.tokenize = False

            if setting not in _allowed_settings_keys:
                continue

            # If the current setting has no value, check to see if
            # the object already has an attribute of the same name.
            # If it does not, then we assume this is the original
            # config being loaded, so assign the value.

            # If it the setting has no value and the attribute DOES
            # already exist, then this is a CLI argument and we don't
            # want to overwrite the config... so continue to the next
            # loop iteration.

            if not value:
                try:
                    _ = getattr(self, setting)
                except AttributeError:
                    setattr(self, setting, value)
                else:
                    continue

            setattr(self, setting, value)

    def _get_file_size(self):
        """Return file size in Megabytes."""
        file_ = Path(self.file_name)
        mb = file_.stat().st_size / 1024 / 1024
        return mb

    def scan_file(self, file_name=None):
        """Manage/coordinate the file scan.

        :param file_name: Name of the file to scan.
        """
        start = datetime.now()

        file_to_scan = file_name or self.file_name

        with open(file_to_scan, "r") as rf:
            for index, line in enumerate(rf):

                # If delimiter, then treat file as if it has columns.
                if self.delimiter:
                    self._scan_delimited_line(line, index)
                    continue

                # Treat file as a flat file without columns.
                self._scan_non_delimited_line(line, index)

        end = datetime.now()
        delta = end - start

        logger.info("SUMMARY:")
        logger.info(f"  - Matched regex, failed sanity: {self.failed_sanity}")
        logger.info(f"  - Matched regex, passed sanity: {self.passed_sanity}")

        seconds = delta.seconds
        minutes = delta.seconds // 60

        logger.info(f"Finished in {seconds} seconds (~{minutes} minutes).")

    def _scan_delimited_line(self, line, index):
        """Scan a delimited line.

        :param line: String of text. One line from a file.
        :param index: The line number.
        """
        for filter_ in self.filters:
            column_map = {}

            # Make sure to convert to bytecode/hex if necessary.
            # For example... Start Of Header (SOH).
            delimiter = _byte_code_to_string(self.delimiter)

            columns = line.split(delimiter)

            # Look for matches in each column.
            for i, column in enumerate(columns):
                matches = filter_.regex.findall(column)

                if not matches:
                    continue

                # Fill out column_map
                for match in matches:
                    j = str(i)
                    if j not in column_map:
                        column_map[j] = []

                    column_map[j].append(match)

            for column_number, column_match_list in column_map.items():
                for column_match in column_match_list:

                    if not test_sanity(filter_, column_match):
                        self.failed_sanity += 1

                        if not self.summarize:
                            log_failure(filter_, index)

                        continue

                    self.passed_sanity += 1

                    string_to_log = tokenize(
                        column_match,
                        filter_.token_mask,
                        filter_.token_index,
                        tokenize=self.tokenize,
                        show_matches=self.show_matches,
                    )

                    if not self.summarize:
                        log_success(
                            filter_, index, string_to_log, column=int(column_number)
                        )

    def _scan_non_delimited_line(self, line=None, index=None):
        """Scan string assuming there are no columns/delimiters.

        :param line: The string of text. One line from a text file.
        :param index: The line number.
        """
        for filter_ in self.filters:
            matches = filter_.regex.findall(line)

            if not matches:
                continue

            for match in matches:
                if not test_sanity(filter_, match):
                    self.failed_sanity += 1
                    if not self.summarize:
                        log_failure(filter_, index)
                    continue

                self.passed_sanity += 1

                string_to_log = tokenize(
                    match,
                    filter_.token_mask,
                    filter_.token_index,
                    tokenize=self.tokenize,
                    show_matches=self.show_matches,
                )

                if not self.summarize:
                    log_success(filter_, index, string_to_log)


def test_sanity(filter_, text):
    """Return bool depending on if text passes the sanity check.

    :param filter_: Filter object.
    :param text: The text being tested by the sanity check.

    :return: True or False - Depending on if sanity check passed
        or not.
    """
    for algorithm_name in filter_.sanity:
        if not sanity_check(algorithm_name, text):
            return False
    return True


def log_success(filter_, index, string_, column=None):
    """Log success messages.

    :param filter_: The Filter object.
    :param index: The line number.
    :param string_: The string that matched the filter.
    :param column: Column which the filter matched some text.
    """
    matched_string = string_
    if column:
        message = (
            f"PASSED sanity and matched regex - Filter: {filter_.label}, "
            f"Line {index + 1}, String: {matched_string}, Column: {column + 1}"
        )
    else:
        message = (
            f"PASSED sanity and matched regex - Filter: {filter_.label}, "
            f"Line {index + 1}, String: {matched_string}"
        )
    logger.info(message)


def log_failure(filter_, index, column=None):
    """Log success messages.

    :param filter_: The Filter object.
    :param index: The line number.
    :param column: Column which the filter matched some text.
    """
    if column:
        message = (
            f"FAILED sanity and matched regex - Filter: {filter_.label}, "
            f"Line: {index + 1}, Column: {column + 1}"
        )
    else:
        message = (
            f"FAILED sanity and matched regex - Filter: {filter_.label}, "
            f"Line: {index + 1}"
        )
    logger.debug(message)
