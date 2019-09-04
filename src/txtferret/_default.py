"""Default YAML config.

IF YOU WILL BE CHANGING THIS CONFIG FILE, be sure that you update the
validation functions and tests for _config.py.
"""


DEFAULT_SUBSTITUTE = "[\W_]"
DEFAULT_ENCODING = "utf-8"
DEFAULT_MASK_VALUE = "XXXXXXXXXXXXXXX"
DEFAULT_MASK_INDEX = 0

LOG_HEADERS = "\t".join(
    [
        "date_time",
        "file_path",
        "filter_label",
        "line_num",
        "column_num",
        "string_matched",
    ]
)


DEFAULT_YAML = """
settings:
  mask: No
  log_level: INFO
  summarize: No
  output_file:
  show_matches: Yes
  delimiter:
  ignore_columns:
  file_encoding: 'utf-8'

filters:
  - label: american_express_15_ccn
    type: Credit Card Number
    sanity: luhn
    pattern: '((?:34|37)[0-9]{2}(?:(?:[\W_][0-9]{6}[\W_][0-9]{5})|[0-9]{11}))'
    substitute: '[\W_]'
    exclude_patterns: []
    mask:
      value: XXXXXXXXXXXXX
      index: 2
  - label: visa_16_ccn
    type: Credit Card Number
    sanity: luhn
    pattern: '(4[0-9]{3}(?:(?:[\W_][0-9]{4}){3}|[0-9]{12}))'
    substitute: '[\W_]'
    exclude_patterns: []
    mask:
      value: XXXXXXXXXXXXXXX
      index: 1
  - label: master_card_16_ccn
    type: Credit Card Number
    sanity: luhn
    pattern: '(5[1-5][0-9]{2}(?:(?:[\W_][0-9]{4}){3}|[0-9]{12}))'
    substitute: '[\W_]'
    exclude_patterns: []
    mask:
      value: XXXXXXXXXXXXXX
      index: 2
  - label: discover_16_ccn
    type: Credit Card Number
    sanity: luhn
    pattern: '(6011(?:(?:[\W_][0-9]{4}){3}|[0-9]{12}))'
    substitute: '[\W_]'
    exclude_patterns: []
    mask:
      value: XXXXXXXXXXXX
      index: 4
"""
