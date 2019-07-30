from txtferret.cli import prep_config, bootstrap, get_totals


def test_prep_config():
    def stub_loader(yaml_file=None):
        return {"yaml_file": yaml_file}

    fake_cli_kwargs = {"config_file": "my_test_file"}

    final_config = {"cli_kwargs": {**fake_cli_kwargs}, "yaml_file": "my_test_file"}

    assert prep_config(loader=stub_loader, **fake_cli_kwargs) == final_config


def test_bootstrap():
    class StubClass:
        def __init__(self, _config):
            pass

        def scan_file(self):
            pass

        def summary(self):
            return {"file_name": "hello.txt", "failures": 5, "passes": 5, "time": 28}

    expected = {"file_name": "hello.txt", "failures": 5, "passes": 5, "time": 28}

    config = None

    assert bootstrap(config, StubClass) == expected


def test_get_totals():
    results = [{"failures": 2, "passes": 5}, {"failures": 3, "passes": 10}]

    assert get_totals(results) == (5, 15)
