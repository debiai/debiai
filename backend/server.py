from threading import Timer
from backend.websrv import start_server, open_browser


def run():
    Timer(1, open_browser).start()
    start_server(reloader=False)
