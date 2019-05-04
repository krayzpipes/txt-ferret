import argparse
from datetime import datetime
from pathlib import Path
import re
import sys

from loguru import logger

from config import Config


def luhn(account_string):
    """Checks a string of digits to see if it passes the Luhn test.

    This is an implementation inspired by the Wikipedia article on
    the Luhn algorithm.
    """

    try:
        double_tuple = (0, 2, 4, 6, 8, 1, 3, 5, 7, 9)
        evens = sum(int(even_num) for even_num in account_string[-1::-2])
        odds = sum(double_tuple[int(odd_num)] for odd_num in account_string[-2::-2])
    except ValueError:
        raise ValueError("Account string cannot be converted to integer")
    else:
        return (evens + odds) % 10 == 0

class TxtFerret:
    def __init__(
            self, file_name, tokenize_string=None, ccn_mapping=None, tokenize=True,
            config_=None,
    ):
        self.file_name = file_name
        self._tokenize_string = tokenize_string or "XXXXXXXX"
        self._ccn_regex_mapping = ccn_mapping or {
            "american_express": "((34|37)\d{2}[\W_]?\d{6}[\W_]?\d{5})",
            "visa_newer": "(4\d{3}[\W_]?\d{4}[\W_]?\d{4}[\W_]?\d{4})",
            "master_card": "(5[1-5]\d{2}[\W_]?\d{4}[\W_]?\d{4}[\W_]?\d{4})",
            "discover": "(6011[\W_]?\d{4}[\W_]?\d{4}[\W_]?\d{4})",
            "diners_carte": "((30[0-5]\d|3[68]\d{2})[\W_]?\d{6}[\W_]?\d{4})",
        }
        self._ccn_regex_compiled = {
            k: re.compile(v) for k, v in self._ccn_regex_mapping.items()
        }
        self._tokenize_flag = tokenize
        self.file_size = self._get_file_size
        self.config = config_ or Config()

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
        logger.info(f"Regex matched  but luhn failed summary: {failed_sanity}")
        logger.info(f"Regex matched and luhn passed summary: {passed_sanity}")


    def scan_line(self, index, line):
        _failed_sanity = 0
        _passed_sanity = 0
        for key, regex in self._ccn_regex_compiled.items():
            match = regex.search(line)

            if not match:
                continue

            filtered = re.sub("[\W_]", "", match.group(1))
            luhn_result = luhn(filtered)

            if not luhn_result:
                _failed_sanity += 1
                if not self.config.SUMMARIZE:
                    logger.debug(
                        f"{key} regex matched but luhn tested negative: line {index}."
                    )
                continue
            result_string = self.tokenize(filtered)
            _passed_sanity += 1
            if not self.config.SUMMARIZE:
                logger.info(
                    f"Regex for {key} matched an passed Luhn test on line "
                    f"{index+1}: {result_string}"
                )
        return _failed_sanity, _passed_sanity

    def tokenize(self, clear_text):
        if not self._tokenize_flag:
            return clear_text
        tokenized_text = f"{clear_text[0:4]}{self._tokenize_string}{clear_text[12:]}"
        return tokenized_text


def main():

    file_parser = argparse.ArgumentParser()

    file_parser.add_argument(
        "FILE",
        help="File path/name you wish to analyze.",
        type=str,
    )
    file_parser.add_argument(
        "-nt",
        "--no_tokenize",
        action="store_true",
        help="If switch is present, data output will not be tokenized.",
    )
    file_parser.add_argument(
        "-l",
        "--log_level",
        default="INFO",
        help="Log level (cautious of file size for debug): INFO, WARNING, ERROR, DEBUG",
        type=str,
    )
    file_parser.add_argument(
        "-s",
        "--summarize",
        action="store_true",
        help="Summarize output instead of notifying of every line matched.",
    )
    file_parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="The file you wish to write results to.",
        type=str,
    )

    args = file_parser.parse_args()

    config_ = Config()

    if args.no_tokenize:
        config_.TOKENIZE = False
    if args.log_level in ["INFO", "WARNING", "ERROR", "DEBUG"]:
        config_.LOG_LEVEL = args.log_level
    if args.summarize:
        config_.SUMMARIZE = True
    if args.output:
        config_.OUTPUT_FILE = args.output
    config_.INPUT_FILE = args.FILE

    # print(dir(config_))


    logger.remove()

    logger.add(sys.stderr, level=config_.LOG_LEVEL)

    start = datetime.now()
    ccn_finder = CCNFinder(config_.INPUT_FILE, config_=config_, tokenize=config_.TOKENIZE)
    ccn_finder.scan_file()
    end = datetime.now()
    delta = end - start

    logger.info(
        f"CCN Scan completed for file {ccn_finder.file_name} "
        f"/ {ccn_finder.file_size()} MB in {delta.seconds} seconds.")


if __name__ == '__main__':
    main()
    exit()
