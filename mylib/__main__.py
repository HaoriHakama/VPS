from threading import Thread

import matplotlib
import matplotlib.figure

from mylib.launch_osc_server import launch_osc_server
from mylib.plot_graph import PlotGraph
from mylib.positioning_system import PositioningSystem

matplotlib.use("TkAgg")


if __name__ == "__main__":
    positionig_system = PositioningSystem()

    # OSCの受信処理を開始
    osc_thread = Thread(
        target=launch_osc_server, args=(
            positionig_system, ), daemon=True)
    osc_thread.start()

    # グラフの描画を開始
    # graph = PlotGraph(positionig_system)
    # graph.start_plot_graph()
    while True:
        pass
