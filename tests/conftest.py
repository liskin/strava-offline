import pytest  # type: ignore [import]


@pytest.fixture(scope="session")
def vcr_config():
    return {
        'match_on': ('method', 'scheme', 'host', 'port', 'path', 'query', 'body')
    }
