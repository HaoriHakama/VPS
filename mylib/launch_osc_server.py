import argparse
from pythonosc import dispatcher
from pythonosc import osc_server
from mylib.positioning_system import PositioningSystem


# OSCサーバーを起動する
def launch_osc_server(positioning_system: PositioningSystem):

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1",help="The ip to listen on")
    parser.add_argument("--port", type=int, default=9001,help="The port to listen on")
    args = parser.parse_args()

    dpt = dispatcher.Dispatcher()

    dpt.map("/avatar/parameters/VPS", positioning_system.pys_switch, dpt)

    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dpt)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()

def set_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1",help="The ip to listen on")
    parser.add_argument("--port", type=int, default=9001,help="The port to listen on")
    args = parser.parse_args()

    return args

def set_dpt():
    dpt = dispatcher.Dispatcher()
    return dpt

def set_server(args, dpt):
    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dpt)
    return server

def start_server(server: osc_server.ThreadingOSCUDPServer):
    print("Serving on {}".format(server.server_address))
    server.serve_forever()

def server_stop(server: osc_server.ThreadingOSCUDPServer):
    server.shutdown()
    server.server_close()

