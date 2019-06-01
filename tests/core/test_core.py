from contextlib import contextmanager

from txtferret.core import gzipped_file_check


def test_gzipped_file_check_return_true():

    @contextmanager
    def opener_stub_raise_error(x, y):

        class FileHandlerStub:

            @staticmethod
            def readline():
                raise UnicodeDecodeError("fake", b"o", 1, 2, "fake")

        yield FileHandlerStub()

    assert gzipped_file_check("f.txt", _opener=opener_stub_raise_error) == True


def test_gzipped_file_check_return_false():

    @contextmanager
    def opener_stub_no_error(x, y):

        class FileHandlerStub:

            @staticmethod
            def readline():
                return ""

        yield FileHandlerStub()

    assert gzipped_file_check("f.txt", _opener=opener_stub_no_error) == False
