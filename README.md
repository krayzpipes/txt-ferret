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
(venv) $ python setup.py install
```

```bash
(venv) $ txtferret scan my_file.txt
```

## What is this for?

- Searches files line by line for sensitive data (or non-sensitive data if you prefer).
- Tokenizes data so you don't expand the scope of your data problem by writing sensitive data
to log files or stdout.
- Performs sanity checks on matched data:
    - For example: Credit card numbers can be run through a Luhn algorithm to reduce false positives.

## Configuration

There are two ways to configure txt-ferret. You can make changes or add filters through making a
custom configuration file (based on the default YAML file) or you can add some settings via
CLI switches.

- CLI Switches will always win/take precedence.
- User-defined configuration file will always beat the default configuration.
- If any settings are not defined in a user-file configuration by cli switches, then the default
setting will be applied.


Txt-ferret comes with a default config which you can dump into any directory
you wish and change it or use it for reference. If you change the file, you have to
specifiy it with the appropriate CLI switch in order for the script to use it. See the
CLI section below.

```bash
(venv) $ txtferret dump-config /file/to/write/to.yaml
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
    - Any regular expression compatible with the python `re` library should work.
    - __Note: It is handy to surround your regex with single quotes. I've observed issues
    with pyyaml when single quotes do not surround the regex pattern.__
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
  tokenize: Yes
  log_level: INFO
  summarize: No
  output_file:
  show_matches: Yes
  delimiter:
```




- **tokenize**
    - If set to true, the token mask defined in the filter will be used to mask the data during output.
    - If no mask is set for a filter, the program will tokenize with a default mask.
    - This is set to 'true' by default.
    - **CLI** - The `-nt` switch can be used to turn off tokenization'
    ```bash
    $ txtferret scan ../fake_ccn_data.txt
    2017:05:20-00:24:52:-0400 PASSED sanity and matched regex - Filter: fake_ccn_account_filter, Line 1, String: 10XXXXXXXXXXXXXXXXXXX
  
    $ txtferret scan -nt ../fake_ccn_data.txt
    2017:05:20-00:26:18:-0400 PASSED sanity and matched regex - Filter: fake_ccn_account_filter, Line 1, String: 100102030405060708094
    ```
- **log_level:**
    - This is the log level which you wish to use. `INFO` will only provide output for filters that
    have matched AND passed the associated sanity check(s). `DEBUG` will log both matched/checked filters
    as well as filters that matched but did NOT pass the sanity check(s).
    - **CLI** - The `-l` switch will allow you to change log levels:
    ```bash
    $ txtferret scan ../fake_ccn_data.txt
    2019:05:20-00:36:00:-0400 PASSED sanity and matched regex - Filter: fake_ccn_account_filter, Line 1, String: 10XXXXXXXXXXXXXXXXXXX
  
    $ txtferret scan -l DEBUG ../fake_ccn_data.txt
    2019:05:20-01:02:07:-0400 PASSED sanity and matched regex - Filter: fake_ccn_account_filter, Line 1, String: 10XXXXXXXXXXXXXXXXXXX
    2019:05:20-01:02:07:-0400 FAILED sanity and matched regex - Filter: fake_ccn_account_filter, Line: 2
    ```
- **summarize**
    - If set to true, the script will only output a list of three data points:
        - The number of matches that did not pass sanity checks.
        - The number of matches that did pass sanity checks.
        - The time it took to finish searching the file.
    - **CLI** - The `-s` switch will kickoff the summary.
    ```bash
    $ txtferret scan ../fake_ccn_data.txt
    2019:05:20-00:36:00:-0400 PASSED sanity and matched regex - Filter: fake_ccn_account_filter, Line 1, String: 10XXXXXXXXXXXXXXXXXXX
 
    $ txtferret scan -s ../fake_ccn_data.txt
    2019:05:20-01:05:29:-0400 SUMMARY:
    2019:05:20-01:05:29:-0400   - Matched regex, failed sanity: 1
    2019:05:20-01:05:29:-0400   - Matched regex, passed sanity: 1
    2019:05:20-01:05:29:-0400 Finished in 0 seconds (~0 minutes)
    
    ```
- **output_file**
    - Add the absolute path to a file in which you would like to write results to.
    - **CLI** - Use the `-o` switch to set an output file.
    ```bash
    $ txtferret scan -o my_output.log file_to_scan.txt
    ```
- **show_matches**
    - If this is set to 'No', then it will redact the matched string all-together in output.
    Be careful that you do not override this setting via a CLI switch unless it is on purpose.
- **delimiter**
    - Define a delimiter. This delimiter will be used to split each line from the txt file into
    columns. Then txtferret will apply regex filters to each field instead of the entire line.
    NOTE: THIS GREATLY SLOWS DOWN THIS SCRIPT. One benefit of this functionality is that the
    output will provide you with the column in which the regex matched.
    - You can define a byte-code delimiter by using `b` followed by the code. For example, `b1` will
    use Start of Header as a delimiter (\x01 in hex)
    - **CLI** - Use the `-d` switch to set a delimiter and scan per column instead of line.
    ```bash
    $ txtferret scan ../fake_ccn_data.txt
    2019:05:20-00:36:00:-0400 PASSED sanity and matched regex - Filter: fake_ccn_account_filter, Line 1, String: 10XXXXXXXXXXXXXXXXXXX

    $ txtferret scan -d , ../fake_ccn_CSV_file.csv
    2019:05:20-01:12:18:-0400 PASSED sanity and matched regex - Filter: fake_ccn_account_filter, Line 1, String: 10XXXXXXXXXXXXXXXXXXX, Column: 3
    ```

# Development

## Running Tests

```bash
$ pytest txt-ferret/tests/
```

