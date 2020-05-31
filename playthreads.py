#! /usr/bin/env python3
import logging
import threading
from threading import Event
from queue import Queue
import time
import random
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler

class EnqueueHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        logging.info("sending headers")
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        logging.info("enqueueing job")
        jobs.put(("webjob", random.randint(1,9)))
        self.wfile.write("Hello world")
        return

def serial(name):
    logging.info("awoken")
    while True:
        job = jobs.get()
        logging.info(f"doing work {job[0]} ({job[1]}):")
        time.sleep(job[1])
        if job[0] == "shutdown":
            break
    logging.info("shutdown and cleanup complete")

def webserver(handler_class):
    server_class=HTTPServer
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    logging.info("starting")
    while not shutdown_recieved.is_set():
        logging.info("starting to handle request")
        httpd.handle_request()
        logging.info("finished handling request")


if __name__ == "__main__":
    format = "%(asctime)s: %(funcName)s - %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    logging.info("starting serial_thread")
    jobs = Queue()
    shutdown_recieved = Event()
    s = threading.Thread(target=serial, args=(1,))
    w = threading.Thread(target=webserver, args=(EnqueueHandler))
    s.start()
    w.start()
    try:
        while True:
            logging.info("doing stuff")
            time.sleep(random.randint(1,9))
            jobs.put(("mainjob", random.randint(1,9)))
    except (KeyboardInterrupt, SystemExit):
        logging.info("KeyboardInterrupt or SystemExit, shutting down main thread")
        jobs.put(("shutdown", 0))
        shutdown_recieved.set()

    logging.info("waiting for threads to finish")
    s.join()
    w.join()
    logging.info("all done")
