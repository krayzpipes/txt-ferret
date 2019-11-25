"""Core classes and functions for txt_ferret."""

from datetime import datetime
import gzip
import os
from pathlib import Path
import re

from loguru import logger

from ._config import ALLOWED_SETTINGS_KEYS
from ._sanity import sanity_check
from ._default import (
    DEFAULT_SUBSTITUTE,
    DEFAULT_ENCODING,
    DEFAULT_MASK_INDEX,
    DEFAULT_MASK_VALUE,
    LOG_HEADERS,
)


CURRENT_DIR = dir


def mask(
    clear_text,
    mask_value,
    index,
    mask=False,
    show_matches=False,
    encoding_=DEFAULT_ENCODING,
    mask_func=None,
):
    """Return string as redacted, masked format, or clear text.

    :param clear_text: The text to be masked.
    :param mask: The mask to be applied to the clear text.
    :param index: Which index in the clear_text string the mask should
        start at.
    :param mask: Bool representing whether the clear text should be
        masked or not.
    :param show_matches: Bool representing whether the clear text should
        be redacted all together or not.
    :param encoding_: Encoding of the text which will be masked.
    """

    if not show_matches:
        return "REDACTED"

    if not mask:
        return clear_text

    mask_function = mask_func or _get_masked_string

    # Convert to str so we can use it like a list with indexes natively.
    _clear_text = clear_text.decode(encoding_)
    _mask_value = mask_value.decode(encoding_)

    return mask_function(_clear_text, _mask_value, index).encode(encoding_)


def _get_masked_string(text, mask_value, index):
    """Return masked string.

    :Note: If the mask length will cause the final string to be longer
        than the original string, then the mask will be cut down to
        size.
    """

    end_index = index + len(mask_value)
    text_length = len(text)
    if (text_length - 1) < end_index:
        temp_string = f"{text[:index]}{mask_value}"
        return temp_string[:text_length]
    return f"{text[:index]}{mask_value}{text[end_index:]}"


def _byte_code_to_string(byte_code, _encoding):
    """Return the UTF-8 form of a byte code.

    :param byte_code: String that may contain a string that matches the
        bytcode format defined by txt-ferret. (Ex: Start of Header would
        be passed into this function as 'b01' instead of '\x01' as
        there are issues passing backslashes through the CLI arguments.

    :return: UTF-8 version of byte-code.
    """
    match = re.match(b"b([0-9]{1,3})", byte_code)
    if not match:
        return byte_code
    code_ = int(match.group(1))
    return bytes((code_,))


def gzipped_file_check(file_to_scan, _opener=None):
    """ Return bool based on if opening file having first two
    gzip chars.

    If the first two bytes are \x1f\x8b, then it is a gzip file.

    :param file_to_scan: String containing file path/name to read.
    :param _opener: Used to pass file handler stub for testing.

    :return: True if first two bytes match first two bytes of gzip file.
    """

    # Use test stub or the normal 'open'
    _open = _opener or open

    # Read first two bytes
    with _open(file_to_scan, "rb") as rf:
        first_two_bytes = rf.read(2)

    gzip_bytes = b"\x1f\x8b"

    if first_two_bytes == gzip_bytes:
        return True
    return False


class Filter:
    """ Helper class to  hold filter configurations and add a simple
    API to interface with Filter attributes.

    :attribute label: The name of the filter in question.
    :attribute pattern: The regular expression that will be used to
        match text.
    :attribute substitute: The regular expression used to replace
        characters within the matched string (like a delimiter).
    :attribute type: A classification of the filter.
    :attribute sanity: The name of the sanity check (ex: 'luhn').
    :attribute mask_value: Mask used to mask filter results.
    :attribute mask_index: Index in clear-text string in which the
        mask should start being applied.
    """

    def __init__(self, filter_dict, gzip, _encoding=DEFAULT_ENCODING):
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

        try:
            self.substitute = filter_dict["substitute"]
        except KeyError:
            self.substitute = DEFAULT_SUBSTITUTE
        else:
            if not self.substitute or self.substitute is None:
                self.substitute = DEFAULT_SUBSTITUTE

        self.type = filter_dict.get("type", "NOT_DEFINED")
        self.sanity = filter_dict.get("sanity", "")
        self.empty = ""  # Used in re.sub in 'sanity_check'

        # Sanity should be a list of strings. If just a string, convert
        # it to a list with a single element.
        if isinstance(self.sanity, str):
            self.sanity = [self.sanity]

        try:
            self.mask_value = filter_dict["mask"].get("value", DEFAULT_MASK_VALUE)
        except KeyError:
            self.mask_value = DEFAULT_MASK_VALUE  # move this to the default
            self.mask_index = DEFAULT_MASK_INDEX
            logger.info(
                f"Filter did not have mask section. Reverting to "
                f"default masking value and index."
            )
        try:
            _exclude_patterns = filter_dict["exclude_patterns"]
        except KeyError:
            raise ValueError("Excluded patterns not found in config file.")
        else:
            self.exclude_patterns = [
                re.compile(pattern.encode(_encoding)) for pattern in _exclude_patterns
            ]

        self.mask_value = self.mask_value.encode(_encoding)
        self.pattern = self.pattern.encode(_encoding)
        self.substitute = self.substitute.encode(_encoding)
        self.empty = b""  # Used in re.sub in 'sanity_check'

        try:
            self.mask_index = int(filter_dict["mask"].get("index", 0))
        except ValueError:
            raise ValueError(f"Token index for filter is not an integer.")

        self.regex = re.compile(self.pattern)


def results_file_name(file_path, output_dir):
    file_name = os.path.basename(file_path)
    output_path = os.path.join(output_dir, file_name)
    return f"{output_path}.results"


def get_file_path(file_path, output_file):
    _output_dir = os.path.dirname(output_file)
    return results_file_name(file_path, _output_dir)


class TxtFerret:
    """Class to hold state and manage scanning files for data.

    Some attributes are dynamically assigned based on contents of the
    config/settings file or CLI arguments/switches.

    :attribute file_name: The name of the file to scan.
    :attribute gzip: Bool depicting if input file is gzipped
    :attribute mask: Determines if txt_ferret will mask the
        output of strings that match and pass sanity checks.
    :attribute summarize: If True, only outputs summary of the scan
        results.
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

    def __init__(self, config):
        """Initialize the TxtFerret object."""
        cli_settings = config["cli_kwargs"]

        self.file_name = cli_settings["file_name"]
        self.output_file = cli_settings.get("output_file")
        self.file_encoding = cli_settings.get("file_encoding", DEFAULT_ENCODING)
        self.gzip = gzipped_file_check(self.file_name)

        if self.gzip:
            logger.info(
                f"Detected non-text file '{self.file_name}'... "
                f"attempting GZIP mode (slower)."
            )

        if self.output_file:
            file_path = get_file_path(self.file_name, self.output_file)
            self.fh = open(file_path, "w+", encoding=self.file_encoding)
        else:
            self.fh = None

        # TODO - we should explicitly set these settings to avoid
        # TODO - dependency issues/ordering...
        # Set settings from file.
        self.set_attributes(**config["settings"])

        # Override settings from file with CLI arguments if present.
        self.set_attributes(**cli_settings)

        if self.delimiter:
            self.delimiter = self.delimiter.encode(self.file_encoding)

        # Counters
        self.failed_sanity = 0
        self.passed_sanity = 0

        self._time_delta = None

        self.filters = [
            Filter(filter_dict=filter_, gzip=self.gzip) for filter_ in config["filters"]
        ]

    def set_attributes(self, **kwargs):
        """Sets attributes for the TxtFerret object.

        These attributes are based on the YAML config files as well
        as the CLI arguments."""
        for setting, value in kwargs.items():

            if setting == "mask":
                if not value or value is None:
                    self.mask = False
                    continue
                self.mask = True

            if setting not in ALLOWED_SETTINGS_KEYS:
                continue

            # ignore_columns will not be a switch, so we want to go
            # ahead and handle it here instead of trying to determine
            # if it's a cli_argument further down.
            if setting == "ignore_columns":
                if value is not None and value:
                    value = {int(column) for column in value}
                    self.ignore_columns = value

                    # Let the user know which columns are being ignored
                    print_string = ", ".join(
                        [str(col_num) for col_num in sorted(self.ignore_columns)]
                    )
                    log_message = f"Columns set to be ignored: {print_string}"
                    logger.info(log_message)
                    if self.fh is not None:
                        self.fh.write(f"{log_message}\n")

                    continue
                # If it is None or empty, make it an empty set
                self.ignore_columns = set()

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

    def summary(self):
        return {
            "file_name": self.file_name,
            "failures": self.failed_sanity,
            "passes": self.passed_sanity,
            "time": self._time_delta.seconds,
        }

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

        log_message = f"Beginning scan for {file_to_scan}"
        logger.info(log_message)
        if self.fh is not None:
            self.fh.write(f"{log_message}\n")

        log_headers = LOG_HEADERS

        if self.fh is not None:
            self.fh.write(f"{log_headers}\n")

        if not self.gzip:
            _open = open
        else:
            _open = gzip.open

        with _open(file_to_scan, "rb") as rf:
            for index, line in enumerate(rf):

                # if isinstance(line, bytes):
                #    line = str(line)

                # If delimiter, then treat file as if it has columns.
                if self.delimiter:
                    self._scan_delimited_line(line, index)
                    continue

                # Treat file as a flat file without columns.
                self._scan_non_delimited_line(line, index)

        end = datetime.now()
        self._time_delta = end - start

        delta_seconds = str(self._time_delta.seconds)
        delta_minutes = str(self._time_delta.seconds // 60)

        finished_message = (
            f"Finished scan for {self.file_name} in {delta_seconds} seconds "
            f"(~{delta_minutes} minutes)."
        )
        logger.info(finished_message)
        if self.fh is not None:
            self.fh.write(f"{finished_message}\n")
            self.fh.close()

    def _scan_delimited_line(self, line, index):
        """Scan a delimited line.

        :param line: String of text. One line from a file.
        :param index: The line number.
        """
        for filter_ in self.filters:

            # Make sure to convert to bytecode/hex if necessary.
            # For example... Start Of Header (SOH).
            delimiter = _byte_code_to_string(self.delimiter, self.file_encoding)

            columns = line.split(delimiter)

            column_map = get_column_map(
                columns=columns, filter_=filter_, ignore_columns=self.ignore_columns
            )

            for column_number, column_match_list in column_map.items():
                for column_match in column_match_list:

                    if not sanity_test(
                        filter_, column_match, encoding=self.file_encoding
                    ):
                        self.failed_sanity += 1

                        continue

                    self.passed_sanity += 1

                    _string_to_log = mask(
                        column_match,
                        filter_.mask_value,
                        filter_.mask_index,
                        mask=self.mask,
                        encoding_=self.file_encoding,
                        show_matches=self.show_matches,
                    )
                    # Print a str instead of byte-string
                    string_to_log = _string_to_log.decode(self.file_encoding)

                    if not self.summarize:
                        log_success(
                            self.file_name,
                            filter_,
                            index,
                            string_to_log,
                            self.fh,
                            column=int(column_number),
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

                exclusion_found = False
                for exclusion in filter_.exclude_patterns:
                    if exclusion.search(match):
                        exclusion_found = True

                if exclusion_found:
                    continue

                for exclusion_pattern in filter_.exclude_patterns:
                    if exclusion_pattern.search(match):
                        # TODO Add metric for failing exclusions?
                        continue

                if not sanity_test(filter_, match):
                    self.failed_sanity += 1
                    continue

                self.passed_sanity += 1

                _string_to_log = mask(
                    match,
                    filter_.mask_value,
                    filter_.mask_index,
                    mask=self.mask,
                    encoding_=self.file_encoding,
                    show_matches=self.show_matches,
                )

                # Print a str instead of byte-string
                string_to_log = _string_to_log.decode(self.file_encoding)

                if not self.summarize:
                    log_success(
                        self.file_name,
                        filter_,
                        index,
                        string_to_log,
                        file_handler=self.fh,
                    )


# TODO get_column_map needs tests.
def get_column_map(columns=None, filter_=None, ignore_columns=None):
    """ Return a dict containing columns and their regex matches

    :param columns: List of the columns to scan
    :param filter_: The filter object that contains the regular
        expression to use when scanning the column.
    :ignore_columns: A set containing column numbers which should be
        ignored and not scanned.
    """

    column_map = {}

    for i, column in enumerate(columns):

        # Skip this column if the config says to ignore it.
        if (i + 1) in ignore_columns:
            continue

        _matches = filter_.regex.findall(column)

        if not _matches:
            continue

        # Filter out strings that match exclusions.
        final_matches = []
        for match in _matches:
            include = True
            for exclude_pattern in filter_.exclude_patterns:
                if exclude_pattern.search(match):
                    include = False
            if include:
                final_matches.append(match)

        # Fill out the column_map with {"index": "match"}
        for match in final_matches:
            j = str(i)
            # In case there are multiple matches in a column.
            if j not in column_map:
                column_map[j] = []

            column_map[j].append(match)

    return column_map


def sanity_test(filter_, text, sub=True, encoding=DEFAULT_ENCODING, sanity_func=None):
    """Return bool depending on if text passes the sanity check.

    :param filter_: Filter object.
    :param text: The text being tested by the sanity check.
    :param sub: For future use, can be used to skip the substitution
        portion before passing text to sanity checks.
    :param encoding: Encoding of the text that will be checked.
    :sanity_func: Used for tests.

    :return: True or False - Depending on if sanity check passed
        or not.
    """
    _sanity_checker = sanity_func or sanity_check

    if sub:
        _text = re.sub(filter_.substitute, filter_.empty, text)
    else:
        _text = text

    for algorithm_name in filter_.sanity:

        if not _sanity_checker(algorithm_name, _text, encoding=encoding):
            return False
    return True


def log_success(file_name, filter_, index, string_, file_handler, column=None):
    """Log success messages.

    :param filter_: The Filter object.
    :param index: The line number.
    :param string_: The string that matched the filter.
    "param file_handler: File handler to write logs to.
    :param column: Column which the filter matched some text.
    """
    matched_string = string_
    date_time = datetime.now()
    _column = "N/A"
    if column is not None:
        _column = str(column + 1)
    message = "\t".join(
        [
            date_time.ctime(),
            file_name,
            filter_.label,
            str(index + 1),
            _column,
            matched_string,
        ]
    )
    if file_handler is None:
        logger.info(message)
        return
    file_handler.write(f"{message}\n")
