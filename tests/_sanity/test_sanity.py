
import pytest

from txtferret._sanity import luhn, sanity_check



@pytest.fixture(scope="module")
def good_luhn_fake_account_num():
    return "100102030405060708094"

@pytest.fixture(scope="module")
def bad_luhn_fake_account_num():
    return "100102030405060708095"

@pytest.fixture(scope="module")
def good_luhn_fake_account_num_delims():
    return "1-0010-2030-4050-6070-8094"

@pytest.fixture(scope="module")
def bad_luhn_fake_account_num_delims():
    return "1-0010-2030-4050-6070-8095"


def test_luhn_with_passing_account_num(good_luhn_fake_account_num):
    assert luhn(good_luhn_fake_account_num) == True, "Should have returned True"


def test_luhn_with_failing_account_num(bad_luhn_fake_account_num):
    assert luhn(bad_luhn_fake_account_num) == False, "Should have returned False"


def test_luhn_with_passing_account_num_and_delims(good_luhn_fake_account_num_delims):
    assert luhn(good_luhn_fake_account_num_delims) == True, "Should have returned True"


def test_luhn_with_failing_account_num_and_delims(bad_luhn_fake_account_num_delims):
    assert luhn(bad_luhn_fake_account_num_delims) == False, "Should have returned False"


def test_luhn_for_value_error():
    non_int = "123abc"
    with pytest.raises(ValueError) as e_info:
        _ = luhn(non_int)


def test_luhn_for_value_error_with_delimeters():
    non_int_with_delims = "123-abc"
    with pytest.raises(ValueError) as e_info:
        _ = luhn(non_int_with_delims)
