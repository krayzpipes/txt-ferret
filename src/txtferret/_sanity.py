import re


def luhn(account_string):
    """Return bool if string passes Luhn test.

    This is based on the algorithm example found on the wikipedia
    article for luhn algorithm:

    https[:]//en[dot]wikipedia[dot]org/wiki/Luhn_algorithm

    :param account_string: The string of digits to be tested by the
        luhn algorithm.

    :raises ValueError: Input couldn't be converted to int type.

    :return: True or False depending on if account_string passes Luhn
        test.
    """

    # TODO - Is there a more effecient way to do this?
    # if not isinstance(account_string, str):
    #     account_string = account_string.decode("utf-8")

    # no_special_chars = re.sub("[\W_]", "", account_string)

    try:
        # doubled_tuple:
        # Note that each number is the index doubled, OR it is the
        # difference of the index doubled and 9. This is required
        # as part of the luhn calculations.
        doubled_tuple = (0, 2, 4, 6, 8, 1, 3, 5, 7, 9)
        evens = sum(int(even_num) for even_num in account_string[-1::-2])
        odds = sum(doubled_tuple[int(odd_num)] for odd_num in account_string[-2::-2])
    except ValueError:
        raise ValueError("Luhn algorithm input must convert to int.")
    else:
        return (evens + odds) % 10 == 0


# Mapping used in 'sanity_check' function. Future sanity checks need
# to be added to this map.
sanity_mapping = {"luhn": luhn}


def sanity_check(sanity_check_name, data, sanity_map=None):
    """Return bool representing whether the sanity check passed or not.

    :param sanity_check_name: Name of the sanity check to be
        performed. (Ex: 'luhn')
    :param data: Data to be validated by the sanity check.
    :param sanity_map: Map of sanity checks. Mostly here for tests.

    :raises ValueError: Sanity check does not exist.

    :return: True or False depending on if the data passes sanity check.
    """
    _sanity_mapping = sanity_map or sanity_mapping
    try:
        _sanity_algorithm = _sanity_mapping[sanity_check_name]
    except KeyError:
        raise ValueError(f"Sanity algorithm {sanity_check_name} does not exist.")
    else:
        return _sanity_algorithm(data)
