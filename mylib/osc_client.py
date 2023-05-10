import socket
import argparse
from pythonosc import udp_client


def osc_client():

    # ローカルipアドレスの取得
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    str_ip = str(ip)

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default=str_ip, help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=9000, help="The port of the OSC server is listening on")

    args = parser.parse_args()

    client = udp_client.SimpleUDPClient(args.ip, args.port)
    return client