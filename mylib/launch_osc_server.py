import argparse
from pythonosc import dispatcher
from pythonosc import osc_server
from mylib.positioning_system import PositioningSystem
from mylib import plot_graph


# OSCサーバーを起動する
def launch_osc_server(positioning_system: PositioningSystem):

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1",help="The ip to listen on")
    parser.add_argument("--port", type=int, default=9001,help="The port to listen on")
    args = parser.parse_args()

    dpt = dispatcher.Dispatcher()

    positioning_system.dpt_map(dpt)
    # dpt.map("/avatar/parameters/VPS/sat_1/*", print)

    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dpt)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()