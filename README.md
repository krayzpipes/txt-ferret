# txt-ferret
Identify and classify data in your text files with Python.

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

# About

### Definition - Txt-Ferret:
- A weasel-like mammal that feasts on rodents... and social security numbers,
credit card numbers, or any other data that's not supposed to be in your text files.



# What is this for?

- Searches files line by line for sensitive data (or non-sensitive data if you prefer).
- Tokenizes data so you don't expand the scope of your data problem by writing sensitive data
to log files or stdout.
- Performs sanity checks on matched data:
    - For example: Credit card numbers are run through a Luhn algorithm to reduce false positives.


# Why did this come about?

- Most Data Loss Prevention (DLP) and Data Classification products have strict limits on the size of files
that can be classified or scanned. This causes issues when you need to scan entire large files (GBs or TBs)
for sensitive data. For example:
    - AWS Macie has a 3 TB limit per account.
    - AWS Macie will only use the first 20 MB of a file to classify your data... and it only does that if
    your original 'compressed' file is less than 20 MB in size.
    - AWS Macie isn't designed to be used on-prem or on your local machine.
- Yara-inspired
    - Yara is a tool that performs string matching usually when trying to classify malware.
    - Instead of using strictly Yara or using python wrappers for Yara, a pure python solution might be
    easier to maintain with the growing Python community.