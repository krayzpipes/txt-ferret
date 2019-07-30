"""Handle CLI tool configuration and commands."""

import copy
from datetime import datetime
import multiprocessing as mp
import pathlib
import sys

import click
from loguru import logger

from ._config import load_config, save_config
from .core import TxtFerret


def set_logger(**cli_kwargs):
    """Configured logger.

    Sets up handlers for stdout and for output file if the user
    passed an output file name.

    Sets up message format and level.

    :param cli_kwargs: The key/value pairs depicting the CLI arguments
        given by the user.
    """
    # Setup basic log config including a sink for stdout.
    log_config = {
        "handlers": [
            {
                "sink": sys.stdout,
                "format": "<lvl>{time:YYYY:MM:DD-HH:mm:ss:ZZ} {message}</lvl>",
                "level": cli_kwargs["log_level"],
                "enqueue": True,
            }
        ]
    }

    output_file = cli_kwargs["output_file"]

    # If output file is defined, create a sink for it and add it to
    # the logger.
    if output_file is not None:
        output_sink = {
            "sink": output_file,
            "serialize": False,
            "format": "{time:YYYY:MM:DD-HH:mm:ss:ZZ} {message}",
            "level": cli_kwargs["log_level"],
            "enqueue": True,
        }
        log_config["handlers"].append(output_sink)

    logger.configure(**log_config)


def prep_config(loader=None, **cli_kwargs):
    """Return a final config file to be sent to TxtFerret."""
    _loader = loader or load_config
    file_name = cli_kwargs["config_file"]
    config = _loader(yaml_file=file_name)
    config["cli_kwargs"] = {**cli_kwargs}
    return config


def bootstrap(config, test_class=None):
    """Bootstrap scanning a single file and return summary."""
    ferret_class = test_class or TxtFerret
    ferret = ferret_class(config)
    ferret.scan_file()
    return ferret.summary()


def get_files_from_dir(directory=None):
    """Return list of absolute file names."""
    path = pathlib.Path(directory)
    file_names = [str(item.resolve()) for item in path.iterdir() if item.is_file()]
    return file_names


def get_totals(results=None):
    """Return counts for failures and successes."""
    _total_failures = 0
    _total_passes = 0

    for result in results:
        _total_failures += result.get("failures")
        _total_passes += result.get("passes")

    return _total_failures, _total_passes


def log_summary(result=None, file_count=None, results=None):
    """Log summary to logger."""
    failures = result.get("failures")
    passes = result.get("passes")
    logger.info("SUMMARY:")
    logger.info(f"  - Scanned {file_count} file(s).")
    logger.info(f"  - Matched regex, failed sanity: {failures}")
    logger.info(f"  - Matched regex, passed sanity: {passes}")

    seconds = result.get("time")
    minutes = seconds // 60

    logger.info(f"  - Finished in {seconds} seconds (~{minutes} minutes).")

    if results is None:
        return

    logger.info("FILE SUMMARIES:")
    for _result in results:
        _name = _result.get("file_name")
        _failures = _result.get("failures")
        _passes = _result.get("passes")
        _seconds = _result.get("time")
        _mins = _seconds // 60

        logger.info(
            f"Matches: {_passes} passed sanity checks and {_failures} failed, "
            f"Time Elapsed: {_seconds} seconds / ~{_mins} minutes - {_name}"
        )


@click.group()
def cli():
    """Placeholder"""
    pass


@click.command()
@click.option(
    "--no-tokenize",
    "-nt",
    is_flag=True,
    help="When set, the output from the scan will not be tokenized.",
)
@click.option(
    "--log-level",
    "-l",
    default="INFO",
    help="Log level (cautious of file size for debug): INFO, WARNING, ERROR, DEBUG",
)
@click.option("--summarize", "-s", is_flag=True, help="Summarize output")
@click.option(
    "--output-file",
    "-o",
    default=None,
    help="Write output to file specified by this switch.",
)
@click.option(
    "--config-file", "-c", default=None, help="Load user-defined config file."
)
@click.option(
    "--delimiter",
    "-d",
    default="",
    help="Delimiter to use for field parsing instead of line parsing.",
)
@click.option("--bulk", "-b", is_flag=True, help="Scan multiple files in a directory.")
@click.argument("file_name")
def scan(**cli_kwargs):
    """Kicks off scanning of user-defined file(s)."""

    config = prep_config(**cli_kwargs)

    set_logger(**cli_kwargs)

    if not cli_kwargs["bulk"]:

        result = bootstrap(config)

        log_summary(result=result, file_count=1)

    else:

        start = datetime.now()

        file_names = get_files_from_dir(directory=cli_kwargs["file_name"])
        configs = []

        # Generate a config for each file name which can be passed to
        # multiprocessing...
        for file_ in file_names:
            temp_config = copy.deepcopy(config)
            temp_config["cli_kwargs"]["file_name"] = file_
            configs.append(temp_config)

        # Devy out the work to available CPUs
        cpus = mp.cpu_count()
        with mp.Pool(cpus) as p:
            results = p.map(bootstrap, configs)

        end = datetime.now()

        total_failures, total_passes = get_totals(results)

        total_scanned = len(results)

        delta = end - start

        total_result = {
            "failures": total_failures,
            "passes": total_passes,
            "time": delta.seconds,
        }

        log_summary(result=total_result, file_count=total_scanned, results=results)


@click.command()
@click.argument("file_name")
def dump_config(file_name):
    """Writes default config to user-specified file location."""
    config = load_config()
    save_config(config, file_name)


cli.add_command(scan)
cli.add_command(dump_config)
