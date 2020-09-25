from multiprocessing import Process, Queue
from time import sleep
from types import SimpleNamespace
import bottle  # type: ignore
import webbrowser

from . import config


redirect_uri = f"http://{config.http_host}:{config.http_port}/code"
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


def server(queue, authorization_url):
    global shared
    shared.queue = queue
    shared.authorization_url = authorization_url

    bottle.run(host=config.http_host, port=config.http_port)


def get_code(authorization_url):
    q = Queue()
    p = Process(target=server, args=(q, authorization_url))
    p.start()

    sleep(0.2)
    webbrowser.open_new(f"http://{config.http_host}:{config.http_port}/authorize")

    code = q.get()

    sleep(0.2)
    p.terminate()
    p.join()

    return code
