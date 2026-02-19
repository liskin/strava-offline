from multiprocessing import Process
from multiprocessing import Queue
import sys
from time import sleep
from types import SimpleNamespace
import webbrowser

import bottle  # type: ignore [import]

from . import config

shared = SimpleNamespace()


@bottle.route("/")
@bottle.route("/authorize")
def authorize():
    global shared
    bottle.redirect(shared.authorization_url)


@bottle.route("/code")
def code():
    global shared
    shared.queue.put(bottle.request.query.code)

    return "OK"


def server(_shared: SimpleNamespace) -> None:
    global shared
    shared = _shared

    bottle.run(host=shared.config.http_host, port=shared.config.http_port)


def get_code(config: config.StravaApiConfig, authorization_url: str) -> str:
    if not sys.stdin.isatty():
        raise RuntimeError("not interactive, cannot authorize")

    queue: Queue[str] = Queue()

    shared = SimpleNamespace()
    shared.config = config
    shared.queue = queue
    shared.authorization_url = authorization_url

    process = Process(target=server, args=(shared,))
    process.start()

    sleep(0.2)
    webbrowser.open_new(f"http://{config.http_host}:{config.http_port}/authorize")

    code = queue.get()

    sleep(0.2)
    process.terminate()
    process.join()

    return code


def redirect_uri(config: config.StravaApiConfig) -> str:
    return f"http://{config.http_host}:{config.http_port}/code"
