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

### PyPi

1. Install it

    ```bash
    $ pip3 install txtferret
    ```

### Repo
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

### Run it
- Example file size:
    ```bash
    # Decent sized file.
    
    $ ls -alh | grep my_test_file.dat
    -rw-r--r--  1 mrferret ferrets  19G May  7 11:15 my_test_file.dat
    ```

- Scanning the file.
    ```bash
    # Scan the file.
    # Default behavior is to mask the string that was matched.
    
    $ txtferret scan my_test_file.dat
    2019:05:20-22:18:01:-0400 Beginning scan for /home/mrferret/Documents/test_file_1.dat
    2019:05:20-22:18:18:-0400 PASSED sanity and matched regex - /home/mrferret/Documents/test_file_1.dat - Filter: fake_ccn_account_filter, Line 712567, String: 100102030405060708094
    2019:05:20-22:19:09:-0400 Finished scan for /home/mrferret/Documents/test_file_1.dat
    2019:05:20-22:19:09:-0400 SUMMARY:
    2019:05:20-22:19:09:-0400   - Matched regex, failed sanity: 2
    2019:05:20-22:19:09:-0400   - Matched regex, passed sanity: 1
    2019:05:20-22:19:09:-0400 Finished in 78 seconds (~1 minutes).
    ```
- Scanning the file with a delimiter.
    ```bash
    # Break up each line of a CSV into columns by declaring a comma for a delimiter.
    # Scan each field in the row and return column numbers as well as line numbers.
    
    $ txtferret scan --delimiter , test_file_1.csv
    2019:05:20-21:41:57:-0400 Beginning scan for /home/mrferret/Documents/test_file_1.csv
    2019:05:20-21:44:34:-0400 PASSED sanity and matched regex - /home/mrferret/Documents/test_file_1.csv - Filter: fake_ccn_account_filter, Line 712567, String: 100102030405060708094, Column: 171
    2019:05:20-21:49:16:-0400 Finished scan for /home/mrferret/Documents/test_file_1.csv
    2019:05:20-21:49:16:-0400 SUMMARY:
    2019:05:20-21:49:16:-0400   - Matched regex, failed sanity: 2
    2019:05:20-21:49:16:-0400   - Matched regex, passed sanity: 1
    2019:05:20-21:49:16:-0400 Finished in 439 seconds (~7 minutes).
    ```
    - Scan all files in a directory. Write results to a file and `stdout`
    ```bash
    # Uses multiprocessing to speed up scans of a bulk group of files
 
    $ txtferret scan -o bulk_testing.log --bulk ../test_files/
    2019:06:09-15:15:27:-0400 Detected non-text file '/home/mrferret/Documents/test_file_1.dat.gz'... attempting GZIP mode (slower).
    2019:06:09-15:15:27:-0400 Detected non-text file '/home/mrferret/Documents/test_file_2.dat.gz'... attempting GZIP mode (slower).
    2019:06:09-15:15:27:-0400 Beginning scan for /home/mrferret/Documents/test_file_1.dat.gz
    2019:06:09-15:15:27:-0400 Beginning scan for /home/mrferret/Documents/test_file_2.dat.gz
    2019:06:09-15:15:27:-0400 Beginning scan for /home/mrferret/Documents/test_file_3.dat
    2019:06:09-15:15:27:-0400 PASSED sanity and matched regex - /home/mrferret/Documents/test_file_2.dat.gz - Filter: fake_ccn_account_filter, Line 4, String: 100102030405060708094
    2019:06:09-15:15:27:-0400 Finished scan for /home/mrferret/Documents/test_file_2.dat.gz
    2019:06:09-15:16:04:-0400 PASSED sanity and matched regex - /home/mrferret/Documents/test_file_3.dat - Filter: fake_ccn_account_filter, Line 712567, String: 100102030405060708094
    2019:06:09-15:16:51:-0400 PASSED sanity and matched regex - /home/mrferret/Documents/test_file_1.dat.gz - Filter: fake_ccn_account_filter, Line 712567, String: 100102030405060708094
    2019:06:09-15:17:15:-0400 Finished scan for /home/mrferret/Documents/test_file_3.dat
    2019:06:09-15:19:24:-0400 Finished scan for /home/mrferret/Documents/test_file_1.dat.gz
    2019:06:09-15:19:24:-0400 SUMMARY:
    2019:06:09-15:19:24:-0400   - Scanned 3 file(s).
    2019:06:09-15:19:24:-0400   - Matched regex, failed sanity: 16
    2019:06:09-15:19:24:-0400   - Matched regex, passed sanity: 3
    2019:06:09-15:19:24:-0400   - Finished in 236 seconds (~3 minutes).
    2019:06:09-15:19:24:-0400 FILE SUMMARIES:
    2019:06:09-15:19:24:-0400 Matches: 1 passed sanity checks and 2 failed, Time Elapsed: 236 seconds / ~3 minutes - /home/mrferret/Documents/test_file_1.dat.gz
    2019:06:09-15:19:24:-0400 Matches: 1 passed sanity checks and 3 failed, Time Elapsed: 0 seconds / ~0 minutes - /home/mrferret/Documents/test_file_2.dat.gz
    2019:06:09-15:19:24:-0400 Matches: 1 passed sanity checks and 2 failed, Time Elapsed: 107 seconds / ~1 minutes - /home/mrferret/Documents/test_file_3.dat
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
  substitute: '[\W_]'
  sanity: luhn
  mask:
    index: 2,
    value: XXXXXXXX
  type: Credit Card Number
```

- **label:**
    - This will be displayed in the logs when the filter in question has matched a string.
- **pattern:**
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
- **substitute:**
    - Allows you to define what characters are removed from a string before it is passed to the sanity check(s).
    - Must be a valid regular expression.
    - If missing or empty, the default substitute is `[\W_]`.
- **sanity:**
    - This is the algorithm to use with this filter in order to validate the data is really what you're
    looking for. For example, 16 digits might just be a random number and not a credit card. Putting the
    numbers through the `luhn` algorithm will validate they could potentially be an account number and
    reduce false positives.
    - You can also pass through a list of strings that represent algorithms as long as the algorithm exists
    in the library. If not, please add it and make a pull request!
- **mask:**
    - index:
        - This is the position in the matched string in which the masking will begin.
    - value
        - The string which will be used to mask the matched string.
- **type:**
    - This is basically a description of the 'type' of data you're looking for with this filter.

### Settings

```yaml
settings:
  mask: No
  log_level: INFO
  summarize: No
  output_file:
  show_matches: Yes
  delimiter:
  ignore_columns: [1, 5, 6]
  file_encoding: 'utf-8'
```
- **bulk**
    - This setting is accessible via CLI arguments `-b` or `--bulk`.
    - When those switches are used, pass the directory to scan instead of a single file name.
    - Example:
    ```bash
    $ txtferret scan --bulk /home/mrferret/Documents
    ```
- **mask**
    - If set to true, the mask value defined in the filter will be used to mask the data during output.
    - If no mask is set for a filter, the program will mask with a default mask value.
    - This is set to 'true' by default.
    - **CLI** - The `-m` switch can be used to turn on masking'
    ```bash
    $ txtferret scan -m ../fake_ccn_data.txt
    2017:05:20-00:24:52:-0400 PASSED sanity and matched regex - Filter: fake_ccn_account_filter, Line 1, String: 10XXXXXXXXXXXXXXXXXXX
  
    $ txtferret scan ../fake_ccn_data.txt
    2017:05:20-00:26:18:-0400 PASSED sanity and matched regex - Filter: fake_ccn_account_filter, Line 1, String: 100102030405060708094
    ```
- **log_level:**
    - This is the log level which you wish to use. `INFO` will only provide output for filters that
    have matched AND passed the associated sanity check(s). `DEBUG` will log both matched/checked filters
    as well as filters that matched but did NOT pass the sanity check(s).
    - **CLI** - The `-l` switch will allow you to change log levels:
    ```bash
    $ txtferret scan ../fake_ccn_data.txt
    2019:05:20-00:36:00:-0400 PASSED sanity and matched regex - Filter: fake_ccn_account_filter, Line 1, String: 100102030405060708094
  
    $ txtferret scan -l DEBUG ../fake_ccn_data.txt
    2019:05:20-01:02:07:-0400 PASSED sanity and matched regex - Filter: fake_ccn_account_filter, Line 1, String: 100102030405060708094
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
    2019:05:20-00:36:00:-0400 PASSED sanity and matched regex - Filter: fake_ccn_account_filter, Line 1, String: 100102030405060708094
 
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
    2019:05:20-00:36:00:-0400 PASSED sanity and matched regex - Filter: fake_ccn_account_filter, Line 1, String: 100102030405060708094
    
    # Comma delimiter

    $ txtferret scan -d , ../fake_ccn_CSV_file.csv
    2019:05:20-01:12:18:-0400 PASSED sanity and matched regex - Filter: fake_ccn_account_filter, Line 1, String: 100102030405060708094, Column: 3
    ```
 - **ignore_columns**
    - This setting is ignored if the `delimiter` setting or switch is not set.
    - Add a list of integers and txtferret will skip those columns.
    - If `ignore_columns: [2, 6]` is configured and a csv row is `hello,world,how,are,you,doing,today`, then
    `world` and `doing` will not be scanned but will be ignored.
    - This is particularly useful in columnar datasets when you know there is a column that is full of false positives.
 - **file_encoding**
    - Two uses:
        - Used to encode your `delimiter` value to the appropriate encoding of your file.
        - Used to encode the data matched in the file before being applied to sanity check.
    - Default value is `'utf-8'`
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
- __It's free__
    - No contracts
    - No outrageous licensing per GB of data scanned.
- __You can contribute!__

## Releases

#### Version 0.2.1 - 2019-08-11
- Fixed allowed keys bug introduced in v0.2.0
#### Version 0.2.0 - 2019-08-05
- Changed `tokenize` to `mask` because tokenize was a lie.. it's masking.
    - Replaced `--no-tokenize` switch with `--mask` switch.
- Turned masking off by default.

#### Version 0.1.3 - 2019-08-05
- Added `file_encoding` setting for multi-encoding support.
    - Reads in bytes and assumes `'utf-8'` encoding by default.
#### Version 0.1.2 - 2019-08-01
- Fixed bug with regex when reading gzipped files.
#### Version 0.1.1 - 2019-07-30
- Added `substitute` option to filters.
#### Version 0.1.0 - 2019-07-30
- Removed the `config-override` option.
- Added `ignore_columns` setting.
#### Version 0.0.4 - 2019-06-09
- Added bulk file scanning by the `--bulk` switch.
- Added multiprocessing for bulk scanning.
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
