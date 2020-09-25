from multiprocessing import Process, Queue
from time import sleep
import bottle  # type: ignore
import json
import stravalib  # type: ignore
import webbrowser

from . import config


strava = stravalib.Client()
queue = None


@bottle.route("/authorize")
def authorize():
    redirect_uri = f"http://{config.http_host}:{config.http_port}/token"
    authorize_uri = strava.authorization_url(
        client_id=config.strava_client_id,
        redirect_uri=redirect_uri,
        scope=["read", "profile:read_all", "activity:read_all"],
    )
    bottle.redirect(authorize_uri)


@bottle.route("/token")
def authorization_successful():
    token = strava.exchange_code_for_token(
        client_id=config.strava_client_id,
        client_secret=config.strava_client_secret,
        code=bottle.request.query.code,
    )

    global queue
    queue.put(token)

    return str(token)


def server(q):
    global queue
    queue = q

    bottle.run(host=config.http_host, port=config.http_port)


def get_token_oauth():
    q = Queue()
    p = Process(target=server, args=(q,))
    p.start()

    sleep(0.2)
    webbrowser.open_new(f"http://{config.http_host}:{config.http_port}/authorize")

    token = q.get()

    sleep(0.2)
    p.terminate()
    p.join()

    return token


def refresh_token(token):
    return strava.refresh_access_token(
        client_id=config.strava_client_id,
        client_secret=config.strava_client_secret,
        refresh_token=token['refresh_token'],
    )


def load_token():
    try:
        with open("token.json", "r") as f:
            return json.load(f)
    except Exception:
        return None


def save_token(token):
    with open("token.json", "w") as f:
        json.dump(token, f)


def get_token():
    token = load_token()
    if token:
        token = refresh_token(token)
    else:
        token = get_token_oauth()

    save_token(token)
    return token
