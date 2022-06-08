import logging
import threading
import time
import webbrowser

from waitress import serve

from UI.main import app

WAIT_FOR_SERVER_MS = 100
NUM_THREADS = 8
finished_set_up = False


def server_run():
    serve(app.server, threads=NUM_THREADS)


def wait_bar():
    animation = "|/-\\"
    idx = 0
    while not finished_set_up:
        print(animation[idx % len(animation)], end="\r")
        idx += 1
        idx %= len(animation)
        time.sleep(0.1)


if __name__ == '__main__':
    logging.info("Starting Server")
    thread_wait_bat = threading.Thread(target=wait_bar)
    thread_wait_bat.start()
    server_thread = threading.Thread(target=server_run)
    server_thread.start()  # start dash app on port
    logging.info("Waiting for Server")
    logging.info("Starting Client")
    url = '127.0.0.1:8080'
    try:
        webbrowser.get('C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s').open(url)
    except:
        logging.info("Could not load Chrome automatically, please navigate to 127.0.0.1:8080 manually")
    finished_set_up = True
    server_thread.join()
