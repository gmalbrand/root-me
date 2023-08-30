import socket
import logging
import argparse
import threading
import time
logger = logging.getLogger(__name__)


class Defaults:
    TIMEOUT = 1
    SLEEP_TIME = 0
    IGNORE_WAIT = True
    NON_BLOCKING = False
    BUFFER_SIZE = 4096
    BACKLOG_SIZE = 5
    PORT = 6060
    ENCODING = 'ascii'
    DAEMON = False


class ServerThread(threading.Thread):

    def __init__(self, port, daemon=Defaults.DAEMON, timeout=Defaults.TIMEOUT, sleep_time=Defaults.SLEEP_TIME, ignore_wait=Defaults.IGNORE_WAIT, non_blocking=Defaults.NON_BLOCKING, buffer_size=Defaults.BUFFER_SIZE):
        threading.Thread.__init__(self)
        self.server = socket.gethostname()
        self.port = port
        self.timeout = timeout
        self.sleep_time = sleep_time
        self.ignore_wait = ignore_wait
        self.non_blocking = non_blocking
        self.buffer_size = buffer_size
        self.daemon = daemon

    def run(self):
        pass


class ClientThread(threading.Thread):
    def __init__(self, server, port, timeout=Defaults.TIMEOUT, sleep_time=Defaults.SLEEP_TIME, ignore_wait=Defaults.IGNORE_WAIT, non_blocking=Defaults.NON_BLOCKING, buffer_size=Defaults.BUFFER_SIZE):
        threading.Thread.__init__(self)
        self.server = server
        self.port = port
        self.timeout = timeout
        self.sleep_time = sleep_time
        self.ignore_wait = ignore_wait
        self.non_blocking = non_blocking
        self.buffer_size = buffer_size

    def run(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.ignore_wait:
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if self.timeout > 0:
            client_socket.settimeout(self.timeout)

        try:
            client_socket.connect((self.server, self.port))
        except Exception as e:
            logger.error(
                "Failed to connect to tcp://{}:{}: {}".format(self.server, self.port, str(e)))
            return

        while True:
            try:
                data = client_socket.recv(self.buffer_size)
                if not data:
                    break
                reply = self.process_data(data)

                if reply:
                    client_socket.sendall(reply.encode(Defaults.ENCODING))

                if self.sleep_time > 0:
                    time.sleep(self.sleep_time)
            except Exception as e:
                logger.error(
                    "Communication error with tcp://{}:{}: {}".format(self.server, self.port, str(e)))

        client_socket.close()

    def process_data(self, data):
        return "Do Nothing\n"


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    # Initiating argument parser
    # Options
    argument_parser.add_argument(
        '-d', '--debug', help="Activate debug logs", action="store_true")
    argument_parser.add_argument(
        "-t", "--timeout", help="Socket timeout in seconds", type=int, default=Defaults.TIMEOUT)
    argument_parser.add_argument(
        "--non-blocking", help="Use non blocking socket", action="store_false", default=Defaults.NON_BLOCKING)
    argument_parser.add_argument(
        "--sleep-time", help="Set loop sleep time", type=int, default=Defaults.SLEEP_TIME
    )
    argument_parser.add_argument(
        "--buffer-size", help="Exchange buffer size", type=int, default=Defaults.BUFFER_SIZE
    )
    argument_parser.add_argument(
        "--ignore-wait", help="Reuse socket address in TIME_WAIT state", action="store_false", default=Defaults.IGNORE_WAIT
    )
    argument_parser.add_argument(
        "--backlog-size", help="Back log size", type=int, default=Defaults.BACKLOG_SIZE
    )
    argument_parser.add_argument(
        "--daemon", help="Start server as dameon", default=Defaults.DAEMON, action="store_true"
    )
    argument_parser.add_argument(
        "-s", "--server-mode", help="Start a server. If not set, start a client connection", action="store_true"
    )

    # Arguments
    argument_parser.add_argument(
        "server", help="Server address. If not set, the program will start a server", default=None
    )
    argument_parser.add_argument(
        "port", help="Server or destination port", type=int, default=Defaults.PORT
    )

    args = argument_parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.ERROR)

    if args.server is None:
        logger.debug("Starting server on port {}".format(args.port))
    else:
        logger.debug(
            "Connection to tcp://{}:{}".format(args.server, args.port))
        thread = ClientThread(args.server, args.port, args.timeout, args.sleep_time,
                              args.ignore_wait, args.non_blocking, args.buffer_size)
        thread.start()
        thread.join()
