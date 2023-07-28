def test_version():
    """
    This is a placeholder test and doesn't test any application logic.
    """
    with open("VERSION") as version_file:
        version = version_file.read().strip()
        assert len(version.split(".")) == 3
