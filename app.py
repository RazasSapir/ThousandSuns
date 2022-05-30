import logging
import threading
import time
import webbrowser

from tqdm import tqdm
from waitress import serve

from UI.main import app

WAIT_FOR_SERVER_MS = 100


def server_run():
    serve(app.server)


if __name__ == '__main__':
    logging.info("Starting Server")
    thread = threading.Thread(target=server_run)
    thread.start()  # start dash app on port
    logging.info("Waiting for Server")
    for _ in tqdm(range(WAIT_FOR_SERVER_MS)):
        time.sleep(0.001)
    logging.info("Starting Client")
    url = '127.0.0.1:8080'
    try:
        webbrowser.get('C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s').open(url)
    except:
        logging.info("Could not load Chrome automatically, please navigate to 127.0.0.1:8080 manually")
    thread.join()
