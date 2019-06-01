# txtferret
Identify and classify data in your text files with Python.

## Description
**Definition:** txtferret
- A weasel-like mammal that feasts on rodents... and apparently social security numbers,
credit card numbers, or any other data that's in your text or gzipped text files.

Use custom regular expressions and sanity checks (ex: `luhn` algorithm for account numbers) to find
sensitive data in virtually any size file via your command line.

Why use txtferret?  See the __How/why did this come about?__ section below.

# Table of Contents
- Quick Start
- Configuration
- How/why did this come about?
- Development

# Quick Start

1. Clone it.
    ```bash
    $ git clone git@github.com:krayzpipes/txt-ferret.git
    $ cd txt-ferret
    ```
2. Setup environment.
    ```bash
    $ python3.7 -m venv venv
    $ source venv/bin/activate
    ```
3. Install it.
    ```bash
    (venv) $ python setup.py install
    ```
4. Run it.

    ```bash
    # Decent sized file.
    
    $ ls -alh | grep my_test_file.dat
    -rw-r--r--  1 mrferret ferrets  19G May  7 11:15 my_test_file.dat
    ```
    ```bash
    # Scan the file.
    # Default behavior is to mask the string that was matched.
    
    $ txtferret scan my_test_file.dat
    2019:05:20-22:18:18:-0400 PASSED sanity and matched regex - Filter: visa_16_ccn, Line 712567, String: 4XXXXXXXXXXXXXXX
    2019:05:20-22:19:09:-0400 SUMMARY:
    2019:05:20-22:19:09:-0400   - Matched regex, failed sanity: 2
    2019:05:20-22:19:09:-0400   - Matched regex, passed sanity: 1
    2019:05:20-22:19:09:-0400 Finished in 78 seconds (~1 minutes).
    ```
    ```bash
    # Break up each line of a CSV into columns by declaring a comma for a delimiter.
    # Scan each field in the row and return column numbers as well as line numbers.
    
    $ txtferret scan --delimiter , my_test_file.dat
    2019:05:20-21:44:34:-0400 PASSED sanity and matched regex - Filter: visa_16_ccn, Line 712567, String: 4XXXXXXXXXXXXXXX, Column: 171
    2019:05:20-21:49:16:-0400 SUMMARY:
    2019:05:20-21:49:16:-0400   - Matched regex, failed sanity: 2
    2019:05:20-21:49:16:-0400   - Matched regex, passed sanity: 1
    2019:05:20-21:49:16:-0400 Finished in 439 seconds (~7 minutes).
    ```

# Configuration

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

### Filters

Filters are regular expressions with some metadata. You can use this metadata to
perform sanity checks on regex matches to sift out false positives. (Ex: luhn
algorithm for credit card numbers). You can also mask the output of the matched string 
as it is logged to a file or displayed on a terminal.

```yaml
filters:
- label: american_express_15_ccn
  pattern: '((?:34|37)\d{2}(?:(?:[\W_]\d{6}[\W_]\d{5})|\d{11}))'
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
    - Regular expression must be compatible with the python `re` module in the standard library.
    - Be sure that your regular expression only contains ONE and ONLY ONE capture group. For example,
    if you are capturing a phone number:
        - Don't do this: `'(555-(867|555)-5309)'`
        - Do this: `'(555-(?:867|555)-5309)'`
        - The former example has two capture groups, and inner and an outer.
        - The latter has one capture group (the outer). The inner is a non-capturing
        group as defined by starting the capture group with `?:`.
    - __Note: If you run into issues with loading a custom filter, try adding
    single-quotes around your regular expression.__
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
- **Type:**
    - This is basically a description of the 'type' of data you're looking for with this filter.

### Settings

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
    columns. The output of the script will provide you with the column in which the regex matched in
    addition to the line number.
    - **CAUTION:** Searching by columns GREATLY slows down the script since you are applying a regular
    expression to each column instead of the entire line. 
    - You can define a byte-code delimiter by using `b` followed by the code. For example, `b1` will
    use Start of Header as a delimiter (\x01 in hex)
    - **CLI** - Use the `-d` switch to set a delimiter and scan per column instead of line.
    ```bash
    $ txtferret scan ../fake_ccn_data.txt
    2019:05:20-00:36:00:-0400 PASSED sanity and matched regex - Filter: fake_ccn_account_filter, Line 1, String: 10XXXXXXXXXXXXXXXXXXX
    
    # Comma delimiter

    $ txtferret scan -d , ../fake_ccn_CSV_file.csv
    2019:05:20-01:12:18:-0400 PASSED sanity and matched regex - Filter: fake_ccn_account_filter, Line 1, String: 10XXXXXXXXXXXXXXXXXXX, Column: 3
    ```

# How/why did this come about?

There are a few shortcomings with commercial Data Loss Prevention (DLP) products:
- They often rely on context. It would be too noisy for a commercial solution to alert every time it
matched a sixteen digit string as not all of their customers handle credit card data.
- Many vendors don't have a cheap method of handling large files over 1 GB. Even less can handle
files that are many GBs in size.
- Some DLP solutions will only classify data files based on the first so many megabytes.
- Many DLP solutions are black boxes of magic that do not give you say in what they are looking for
in your data or how they know what they're looking at.

Txtferret was born out after realizing some of these limitations. It isn't perfect, but it's a great
sanity check which can be paired with a DLP solution. Here are some things it was designed to do:
- __Virtually no size limitation__
    - Can run against any size file as long as you can fit it on a drive.
    - It's python... so... no speed guarantee on huge files, but at least it will eventually get it done.
    We've found that txtferret can scan a ~20 GB file between 1 and 3 minutes on our systems.
- __Customizable__
    - Define your own regular expressions and pair them with a sanity check. For example, using the
    built-in `luhn` algorithm will sift out many false positives for credit card numbers. The matched
    credit card number will be run through the `luhn` algorithm first. If it doesn't pass, it is discarded.
- __No context needed__
    - Yeah, this can cause a lot of false positives with certain files; However,
    if you're dealing with a file that doesn't contain context like 'VISA' or 'CVE', then you need
    to start somewhere.
- __Helpful output__
    - Indicates which line the string was found.
    - Indicates which column if you've defined a delimiter (ex: comma for CSV files).
    - You can choose to mask your output data to make sure you're not putting sensitive data
    into your log files or outputting them to your terminal.
    - You can also turn off masking/tokenization so that you can see exactly what was matched. 
- __It's free__
    - No contracts
    - No outrageous licensing per GB of data scanned.
- __You can contribute!__

## Releases

#### Version 0.0.3 - 2019-06-01
- Added gzip detection and support.


# Development
Some info about development.

## Running Tests

```bash
$ pytest txt-ferret/tests/
```

## Contributing
#### Process
1. Create an issue.
2. Fork the repo.
3. Do your work.
4. **WRITE TESTS**
4. Make a pull request.
    - Preferably, include the issue # in the pull request.

#### Style
- Black for formatting.
- Pylint for linting.

# License
See [License](LICENSE)
