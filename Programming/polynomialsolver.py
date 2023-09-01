import re
import math
import socket

ENCODING = 'UTF-8'

equation_rex = re.compile(
    r".*\(([0-9]+)/([0-9]+)\)[^:]+:\s*(-?\s*[0-9]+)\.x²\s*([+-]\s*[0-9]+).x¹\s*\s*([+-]\s*[0-9]+)\s*=\s*(-?\s*[0-9]+)")


def polynomial_solver(data, encoding=ENCODING):
    extraction = equation_rex.search(data.decode(encoding))
    A = int(extraction.group(3).replace(" ", ""))
    B = int(extraction.group(4).replace(" ", ""))
    C = int(extraction.group(5).replace(" ", ""))
    D = int(extraction.group(6).replace(" ", ""))

    delta = B*B - (4*A*(C-D))

    if delta < 0:
        return "Not possible\n".encode(encoding)
    if delta == 0:
        return "{}\n".format(round(-B/(2*A), 3)).encode(encoding)

    return "x1: {} ; x2: {}\n".format(
        round((-B - math.sqrt(delta)) / (2 * A), 3),
        round((-B + math.sqrt(delta)) / (2 * A), 3)).encode(encoding)


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('challenge01.root-me.org', 52018))
        eq_num = 0
        while True:
            data = s.recv(1024)

            if not data or len(data) == 0:
                break

            if not (data[0] == ord("\n") or data[0] == ord("[")):
                print(data.decode())
                break

            eq_num += 1
            try:
                result = polynomial_solver(data)
                s.sendall(result)
            except Exception as e:
                print(data.decode())

        s.close()
        print("{} equations solved".format(eq_num))
