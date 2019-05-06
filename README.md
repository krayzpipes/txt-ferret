# txt-ferret
Identify and classify data in your text files with Python.

**Definition:**
- A weasel-like mammal that feasts on rodents... and apparently social security numbers,
credit card numbers, or any other data that's not supposed to be in your text files.

# Quick Start

```bash
$ git clone git@github.com:krayzpipes/txt-ferret.git
$ cd txt-ferret
```

```bash
$ python3.7 -m venv venv
$ source venv/bin/activate
```

```bash
(venv) $ pip install -r requirements.txt
```

```bash
(venv) $ python txtferret.py scan my_file.txt
```

## What is this for?

- Searches files line by line for sensitive data (or non-sensitive data if you prefer).
- Tokenizes data so you don't expand the scope of your data problem by writing sensitive data
to log files or stdout.
- Performs sanity checks on matched data:
    - For example: Credit card numbers are run through a Luhn algorithm to reduce false positives.

## Configuration

There are two ways to configure txt-ferret. You can make changes or add filters through making a
custom configuration file (based on the default YAML file) or you can add some settings via
CLI switches.

### Configuration file

Txt-ferret comes with a default yaml config file which you can dump into any directory
you wish and change it or use it for reference. If you change the file, you have to
specifiy it with the appropriate CLI switch in order for the script to use it. See the
CLI section below.

```bash
(venv) $ python txtferret dump-config /file/to/write/to.yaml
```
There are two sections of the config file: `filters` and `settings`.

Filters have a number of parts:

```yaml
filters:
- label: american_express_15_ccn
  pattern: '((34|37)\d{2}[\W_]?\d{6}[\W_]?\d{5})'
  sanity: luhn
  tokenize:
    index: 2,
    mask: XXXXXXXX
  type: Credit Card Number
```

- **Label:**
    - This will be displayed in the logs when the filter in question has matched a string.
- **Pattern:**
    - The regular expression which will be used to find data in the file.
    - __Note: Must have a single quote on
    each end for the pyyaml library to use it correctly.__
- **Sanity:**
    - This is the algorithm to use with this filter in order to validate the data is really what you're
    looking for. For example, 16 digits might just be a random number and not a credit card. Putting the
    numbers through the `luhn` algorithm will validate they could potentially be an account number and
    reduce false positives.
    - You can also pass through a list of strings that represent algorithms as long as the algorithm exists
    in the library. If not, please add it and make a pull request!
- **Tokenize:**
    - index:
        - This is the position in the matched string in which the tokenization will begin.
    - mask
        - The string which will be used to tokenize the matched string.
- **type:**
    - This is basically a description of the 'type' of data you're looking for with this filter.


```yaml
settings:
  log_level: INFO
  output_file: null
  summarize: false
  tokenize: true
```

- **log_level:**
    - This is the log level which you wish to use. `INFO` will only provide output for filters that
    have matchad AND passed the associated sanity check(s). `DEBUG` will log both matched/check filters
    as well as filters that matched but did NOT pass the sanity check(s).
- **output_file**
    - Add the absolute path to a file in which you would like to write results to.
- **summarize**
    - If set to true, the script will only output a list of three data points:
        - The number of matches that did not pass sanity checks.
        - The number of matches that did pass sanity checks.
        - The time it took to finish searching the file.
- **tokenize**
    - If set to true, the token mask defined in the filter will be used to mask the data during output.
    - If no mask is set for a filter, the program will tokenize with a default mask.
    - This is set to 'true' by default.

### Configuration via CLI

You can configure the script through various switches when calling the script via the CLI. **NOTE:** The
switches must be used with each call. If you do not use the switches, the default configuration will be used.

For example, you can use a custom config file which you may have changed settings or added new filters to be
used in addition to the existing filters:

```bash
(venv) $ python txtferret.py scan --config-file custom_config.yaml file_to_scan.txt
```

Or you may want to completely override the default filters and ONLY use the filters you have defined:

```bash
(venv) $ python txtferret.py scan --config-file custom_config.yaml --config-override file_to_scan.txt
```

You can also change items in the `settings` portion of the config file just by using switches. Here is output
from the CLI help file:

You can see these options by running the following command:

```bash
(venv) $ python txtferret.py scan --help
```

