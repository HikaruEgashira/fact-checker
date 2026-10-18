from importlib.metadata import version


def test_syrupy_is_version_6():
    assert int(version("syrupy").split(".")[0]) == 6


def test_amber_serialization(snapshot):
    assert '{"id":"***","status":"pending","output":""}' == snapshot
