
"""Default YAML config.

IF YOU WILL BE CHANGING THIS CONFIG FILE, be sure that you update the
validation functions and tests for _config.py.
"""


default_substitute = "[\W_]"


default_yaml = """
settings:
  tokenize: Yes
  log_level: INFO
  summarize: No
  output_file:
  show_matches: Yes
  delimiter:
  ignore_columns:

filters:
  - label: american_express_15_ccn
    type: Credit Card Number
    sanity: luhn
    pattern: '((?:34|37)\d{2}(?:(?:[\W_]\d{6}[\W_]\d{5})|\d{11}))'
    substitute: '[\W_]'
    tokenize:
      mask: XXXXXXXXXXXXX
      index: 2
  - label: visa_16_ccn
    type: Credit Card Number
    sanity: luhn
    pattern: '(4\d{3}(?:(?:[\W_]\d{4}){3}|\d{12}))'
    substitute: '[\W_]'
    tokenize:
      mask: XXXXXXXXXXXXXXX
      index: 1
  - label: master_card_16_ccn
    type: Credit Card Number
    sanity: luhn
    pattern: '(5[1-5]\d{2}(?:(?:[\W_]\d{4}){3}|\d{12}))'
    substitute: '[\W_]'
    tokenize:
      mask: XXXXXXXXXXXXXX
      index: 2
  - label: discover_16_ccn
    type: Credit Card Number
    sanity: luhn
    pattern: '(6011(?:(?:[\W_]\d{4}){3}|\d{12}))'
    substitute: '[\W_]'
    tokenize:
      mask: XXXXXXXXXXXX
      index: 4
  - label: diners_carte_14_ccn
    type: Credit Card Number
    sanity: luhn
    pattern: '((?:30[0-5]\d|3[68]\d{2})(?:(?:[\W_]\d{6}[\W_]\d{4})|\d{10}))'
    substitute: '[\W_]'
    tokenize:
      mask: XXXXXXXXXXXX
      index: 2
"""