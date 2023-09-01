import socket
import logging
import argparse
import threading
import time
logger = logging.getLogger(__name__)


class Defaults:
    TIMEOUT = 0.01
    SLEEP_TIME = 0
    IGNORE_WAIT = True
    NON_BLOCKING = False
    BUFFER_SIZE = 4096
    BACKLOG_SIZE = 5
    PORT = 6060
    ENCODING = 'ascii'
    DAEMON = False


def create_socket(ignore_wait=Defaults.IGNORE_WAIT, timeout=Defaults.TIMEOUT, non_blocking=Defaults.NON_BLOCKING):
    result = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if ignore_wait:
        result.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    result.setblocking(not non_blocking)

    if timeout > 0:
        result.settimeout(timeout)

    return result


def run_client(client_socket, server, port, process_data=lambda x: "Do nothing\n", buffer_size=Defaults.BUFFER_SIZE, sleep_time=Defaults.SLEEP_TIME):
    try:
        logger.debug(
            "Connecting to tcp://{}:{}".format(args.server, args.port))
        client_socket.connect((server, port))
    except Exception as e:
        logger.error(
            "Failed to connect to tcp://{}:{}: {}".format(server, port, str(e)))
        return

    while True:
        try:
            data = client_socket.recv(buffer_size)
            if not data:
                break
            reply = process_data(data)

            if reply:
                client_socket.sendall(reply.encode(Defaults.ENCODING))

            if sleep_time > 0:
                time.sleep(sleep_time)
        except TimeoutError:
            continue
        except KeyboardInterrupt:
            logger.info("Shutting down server")
            break
        except Exception as e:
            logger.error(
                "Communication error with tcp://{}:{}: {} {}".format(server, port, str(e)))

    client_socket.close()


class ClientThread(threading.Thread):

    def __init__(self, client: socket.socket, stop_event: threading.Event, process_data, sleep_time=Defaults.BUFFER_SIZE, buffer_size=Defaults.BUFFER_SIZE):
        threading.Thread.__init__(self)
        self.buffer_size = buffer_size
        self.sleep_time = sleep_time
        self.stop_event = stop_event

    def run(self):
        while True:
            pass


def run_server(server_socket: socket.socket, port: int, process_data=lambda x: "Server does nothing\n", timeout=Defaults.timeout, backlog=Defaults.BACKLOG_SIZE, buffer_size=Defaults.BUFFER_SIZE, sleep_time=Defaults.SLEEP_TIME):
    try:

        logger.debug(
            "Binding on tcp://{}:{}".format(socket.gethostname(), port))
        server_socket.bind((socket.gethostname(), port))
    except Exception as e:
        logger.error(
            "Failed to bind on tcp://{}:{}: {}".format(socket.gethostname(), port, str(e)))
        return

    if backlog > 0:
        server_socket.listen(backlog)

    stop_event = threading.Event()
    while True:

        client, address = server_socket.accept()
        logger.debug(
            "Connection from tcp://{}:{}".format(address[0], address[1]))

        if timeout > 0:
            client.settimeout(timeout)
        ClientThread(client, stop_event, process_data,
                     sleep_time=sleep_time, buffer_size=buffer_size).start()

        if sleep_time > 0:
            time.sleep(sleep_time)
        break
    server_socket.close()


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

    socket = create_socket(ignore_wait=args.ignore_wait,
                           timeout=args.timeout, non_blocking=args.non_blocking)

    if args.server is None:
        logger.debug("Starting server on port {}".format(args.port))
    else:
        run_client(socket, args.server, args.port,
                   buffer_size=args.buffer_size, sleep_time=args.sleep_time)
