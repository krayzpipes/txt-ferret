from contextlib import contextmanager

import pytest

from txtferret.core import (
    gzipped_file_check,
    tokenize,
    _get_tokenized_string,
    _byte_code_to_string,
    sanity_test,
)


def test_gzipped_file_check_return_true():
    @contextmanager
    def opener_stub_raise_error(x, y):
        class FileHandlerStub:
            @staticmethod
            def read(not_used):
                return b'\x1f\x8b'

        yield FileHandlerStub()

    assert gzipped_file_check("f.txt", _opener=opener_stub_raise_error) == True


def test_gzipped_file_check_return_false():
    @contextmanager
    def opener_stub_no_error(x, y):
        class FileHandlerStub:
            @staticmethod
            def read(not_used):
                return b'NOPE'

        yield FileHandlerStub()

    assert gzipped_file_check("f.txt", _opener=opener_stub_no_error) == False


def test_tokenize_not_show_matches():

    assert tokenize("hello", "XXX", 0, show_matches=False) == "REDACTED"


def test_tokenize_return_clear_text():

    assert tokenize("hello", "XXX", 0, tokenize=False, show_matches=True) == "hello"


def test_tokenize_runs_tokenization_function():
    def stub_func(arg1, arg2, arg3):
        return "stub was called"

    assert (
        tokenize("hello", "XXX", 0, show_matches=True, tokenize_func=stub_func)
        == "stub was called"
    )


def test_tokenize_for_byte_return():
    def stub_func(arg1, arg2, arg3):
        return (arg1, arg2, arg3)

    assert tokenize(
        b"hello", b"XXX", 0, show_matches=True, tokenize_func=stub_func
    ) == ("hello", "XXX", 0)


def test_get_tokenized_string_normal():

    text = "howdy"
    mask = "XXX"
    index = 1

    assert _get_tokenized_string(text, mask, index) == "hXXXy"


def test_get_tokenized_string_mask_too_long():

    text = "howdy"
    mask = "XXXXX"
    index = 1

    assert _get_tokenized_string(text, mask, index) == "hXXXX"


def test_byte_code_to_string_no_byte_string():

    fake_byte_code = b'bhello'

    assert _byte_code_to_string(fake_byte_code, _encoding="utf-8") == fake_byte_code


def test_byte_code_to_string_start_of_header():

    byte_code = b'b1'

    assert _byte_code_to_string(byte_code, _encoding="utf-8") == b'\x01'


def test_sanity_for_failed_sanity_check():
    def stub_func(a, b, encoding):
        return False

    class StubFilter:
        sanity = ["fake"]
        substitute = "who_cares"
        empty = ""

    assert sanity_test(StubFilter, "some_text", sanity_func=stub_func) == False


def test_sanity_for_passed_sanity_checks():
    def stub_func(a, b, encoding):
        return True

    class StubFilter:
        sanity = ["sanity1", "sanity2", "sanity3"]
        substitute = "who_cares"
        empty = ""

    assert sanity_test(StubFilter, "some_text", sanity_func=stub_func)
