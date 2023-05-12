import matplotlib
matplotlib.use("TkAgg")
import matplotlib.figure
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mylib.launch_osc_server import launch_osc_server
from mylib.plot_graph import PlotGraph
from mylib.positioning_system import PositioningSystem
from threading import Thread

if __name__ == "__main__":
    positionig_system = PositioningSystem()

    # OSCの受信処理を開始
    osc_thread = Thread(target=positionig_system.launch_positioning_system, daemon=True)
    osc_thread.start()

    # グラフの描画を開始
    graph = PlotGraph(positionig_system)
    graph.start_plot_graph()