import re
import math
import socket
import io
import base64
import logging
import sys
import base64
import bz2
CHALLENGE_HOST = 'challenge01.root-me.org'
CHALLENGE_PORT = 52017
ENCODING = "UTF-8"
BUFFER_SIZE = 4096

CHALLENGE_PREFIX = "[>]"
WRONG_ANSWER_PREFIX = "[!]"
FLAG_PREFIX = "[+]"

logger = logging.getLogger(__name__)

CURRENT_CHALLENGE = 1
TOTAL_CHALLENGE = 2
CHALLENGE = 3


MORSE_CODE_DICT = {'A': '.-', 'B': '-...',
                   'C': '-.-.', 'D': '-..', 'E': '.',
                   'F': '..-.', 'G': '--.', 'H': '....',
                   'I': '..', 'J': '.---', 'K': '-.-',
                   'L': '.-..', 'M': '--', 'N': '-.',
                   'O': '---', 'P': '.--.', 'Q': '--.-',
                   'R': '.-.', 'S': '...', 'T': '-',
                   'U': '..-', 'V': '...-', 'W': '.--',
                   'X': '-..-', 'Y': '-.--', 'Z': '--..',
                   '1': '.----', '2': '..---', '3': '...--',
                   '4': '....-', '5': '.....', '6': '-....',
                   '7': '--...', '8': '---..', '9': '----.',
                   '0': '-----', ', ': '--..--', '.': '.-.-.-',
                   '?': '..--..', '/': '-..-.', '-': '-....-',
                   '(': '-.--.', ')': '-.--.-'}

MORSE_DICT = {'.-': 'A',
              '-...': 'B',
              '-.-.': 'C',
              '-..': 'D',
              '.': 'E',
              '..-.': 'F',
              '--.': 'G',
              '....': 'H',
              '..': 'I',
              '.---': 'J',
              '-.-': 'K',
              '.-..': 'L',
              '--': 'M',
              '-.': 'N',
              '---': 'O',
              '.--.': 'P',
              '--.-': 'Q',
              '.-.': 'R',
              '...': 'S',
              '-': 'T',
              '..-': 'U',
              '...-': 'V',
              '.--': 'W',
              '-..-': 'X',
              '-.--': 'Y',
              '--..': 'Z',
              '.----': '1',
              '..---': '2',
              '...--': '3',
              '....-': '4',
              '.....': '5',
              '-....': '6',
              '--...': '7',
              '---..': '8',
              '----.': '9',
              '-----': '0',
              '--..--': '.',
              '.-.-.-': '.',
              '..--..': '?',
              '-..-.': '/',
              '-....-': '-',
              '-.--.': '(',
              '-.--.-': ')'}


def decode_morse(message: str) -> bytes:
    if not re.match(r"[\.-/]*", message):
        raise Exception("Not morse message")
    result = ""
    for morse_letter in message.split("/"):
        result += MORSE_DICT[morse_letter]
    return result.lower().encode(ENCODING)


DECODE_FUNCTIONS = [
    base64.b16decode,
    base64.b32decode,
    base64.b64decode,
    base64.b85decode,
    bytes.fromhex,
    decode_morse
]


def various_decode(message: str) -> bytes:
    result = "Unable to decode challenge".encode(ENCODING)

    for f in DECODE_FUNCTIONS:
        try:
            # logger.debug(f"Applying function : {f.__name__}")
            result = f(message)
            result.decode('UTF-8')
        except Exception as e:
            result = "Unable to decode challenge".encode(ENCODING)
            continue
        break

    return result + b"\n"


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger.debug(f"Connecting to tcp://{CHALLENGE_HOST}:{CHALLENGE_PORT}")

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((CHALLENGE_HOST, CHALLENGE_PORT))
    except Exception as e:
        logger.error(f"Connection failed with error : {e}")
        sys.exit()

    try:
        data = client.recv(BUFFER_SIZE)
        if not data:
            raise Exception("No data received")
    except Exception as e:
        logger.error(f"Reading first challenge with error : {e}")
        sys.exit()

    buf = io.StringIO(data.decode(ENCODING))
    challenge = None
    while not challenge:
        line = buf.readline()
        if not line:
            break
        if line.startswith(CHALLENGE_PREFIX):
            challenge = line

    while challenge:
        try:
            groups = re.search(
                r"\[>\]\s*\(([0-9]+)/([0-9]+)\)[^:]*:\s*'([^']*)'", challenge)

            current_challenge = int(groups.group(CURRENT_CHALLENGE))
            total_challenge = int(groups.group(TOTAL_CHALLENGE))
            message = groups.group(CHALLENGE)

            response = various_decode(message)
            logger.debug(
                f"Challenge #{current_challenge} / {total_challenge}: {message} => {response}")

            client.sendall(response)

            data = client.recv(BUFFER_SIZE)

            if not data:
                raise Exception("Empty response from server")
            challenge = data.decode(ENCODING)

            # logger.debug(f"New challenge line ${challenge}$")
            if challenge.startswith(WRONG_ANSWER_PREFIX):
                raise Exception(
                    f"Wrong answer for challenge #{current_challenge}")
            if challenge.startswith(FLAG_PREFIX):
                print(challenge)
                break

        except Exception as e:
            logger.error(f"Challenge failed with error : {e}")
            break
    client.close()
