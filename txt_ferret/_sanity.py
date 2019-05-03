

def luhn(account_string):
    """Checks a string of digits to see if it passes the Luhn test.

    This is
    """

    try:
        doubled_tuple = (0, 2, 4, 6, 8, 1, 3, 5, 7, 9)
        evens = sum(int(even_num) for even_num in account_string[-1::-2])
        odds = sum(doubled_tuple[int(odd_num)] for odd_num in account_string[-2::-2])
    except ValueError:
        raise ValueError("Luhn algorithm input must convert to int.")
    else:
        return (evens + odds) % 10 == 0


sanity_mapping = {
    "luhn": luhn,
}