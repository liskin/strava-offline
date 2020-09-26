from multiprocessing import Process, Queue
from time import sleep
from types import SimpleNamespace
import bottle  # type: ignore
import webbrowser

from .config import Config


shared = SimpleNamespace()


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


def get_code(config: Config, authorization_url: str) -> str:
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


def redirect_uri(config: Config) -> str:
    return f"http://{config.http_host}:{config.http_port}/code"
