import pytest  # type: ignore [import]

from strava_offline import config
from strava_offline import redirect_server
from strava_offline import strava


@pytest.mark.vcr
def test_fetch_token(tmp_path, monkeypatch):
    def mock_get_code(config, authorization_url):
        return 'CODE'

    monkeypatch.setattr(redirect_server, 'get_code', mock_get_code)

    token = tmp_path / "token.json"
    cfg = config.StravaApiConfig(
        strava_token_filename=token,
        strava_client_id='12345',
        strava_client_secret='SECRET',
    )

    api = strava.StravaAPI(config=cfg)
    assert api._session.access_token == 'ACCESS_TOKEN'

    # force token auto refresh
    token = api._session.token
    token['expires_at'] = 1600000000
    api._session.token = token

    athlete = api.get_athlete()
    assert api._session.access_token == 'NEW_ACCESS_TOKEN'
    assert athlete['id']
