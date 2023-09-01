import requests
import socket
import json
import bs4
import re
import time

BUFFER_SIZE = 4096
ENCODING = "UTF-8"
SERVER_ID = "10"


def extract_page_content(soup, groups):
    tag = soup.find(groups["target"])

    if not tag:
        return soup.find(attrs={"name": groups["target"]})["content"]
    return tag.text


def extract_attribute_value(soup, groups):
    soup.find(groups["tag"], attrs={groups["attr"]: groups["value"]})[
        groups["target"]]


def extract_parent_attribute_value(soup, groups):
    soup.find(groups["tag"], attrs={groups["attr"]: groups["value"]}).parent()[
        groups["target"]]


responses = {
    r"What's the page (?P<target>[^\s]*)\?": extract_page_content,
    r"What's the (?P<tag>[^']*)'s (?P<target>[^\s]*) value with (?P<attr>[^=]*)=(?P<value>[^?]*)\?": extract_attribute_value,
    r"What's the parent's (?P<target>[^\s]*) value of (?P<tag>[^\s]*) with (?P<attr>[^=]*)=(?P<value>[^?]*)\?": extract_parent_attribute_value
}


if __name__ == "__main__":
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("ctf10.root-me.org", 4444))
        client.recv(BUFFER_SIZE)
        client.recv(BUFFER_SIZE)

        q_num = 1
        while True:
            print('Question 1')
            data = client.recv(BUFFER_SIZE).decode(ENCODING)
            details = json.loads(data)

            resp = requests.get(details["url"].replace(
                "XX", SERVER_ID), cookies=details["cookie"])

            if resp.status_code != 200:
                print(f"Request error : {resp.status_code}")

            soup = bs4.BeautifulSoup(
                resp.content.decode(ENCODING), "html.parser")

            q_id = time.time_ns()
            with open(f"/tmp/question_{q_num}.json", "w") as osf:
                json.dump(details, osf, indent=True)

            with open(f"/tmp/question_{q_num}.html", "w") as ofs:
                ofs.write(soup.prettify())

            response = None
            for r in responses:
                groups = re.search(r, details["question"])
                if groups:
                    response = responses[r](soup, groups)

            if not response:
                print("New question {}".format(details["question"]))
            else:
                client.sendall(f"{response}\n".encode(ENCODING))

                data = client.recv(BUFFER_SIZE).decode[ENCODING]

                print(data)

            q_num += 1
            break
    except Exception as e:
        print(f"Error {e}")
    finally:
        client.close()
