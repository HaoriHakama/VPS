import matplotlib
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

from mylib.positioning_system import PositioningSystem

matplotlib.use("TkAgg")


class PlotGraph:
    def __init__(self, positioning_system: PositioningSystem):
        self.positioning_system = positioning_system
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_xlim(-100, 100)
        self.ax.set_ylim(-100, 100)
        self.ax.set_zlim(-100, 100)
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Z')
        self.ax.set_zlabel('Y')
        self.ax.view_init(elev=90, azim=-90)  # Adjust the viewing angle
        self.x_data, self.y_data, self.z_data = [], [], []
        self.text_template = 'X: {:.1f}, Y: {:.1f}, Z: {:.1f}'
        self.text = plt.figtext(0.05, 0.05, '')

    def update(self, frame):
        if self.positioning_system.datalist is not None and len(
                self.positioning_system.datalist.datalist) > 0:
            self.x_data = self.positioning_system.datalist.x_data()
            self.y_data = self.positioning_system.datalist.y_data()
            self.z_data = self.positioning_system.datalist.z_data()
            self.ax.clear()
            self.ax.set_xlim(-100, 100)
            self.ax.set_ylim(-100, 100)
            self.ax.set_zlim(-100, 100)
            self.ax.set_xlabel('X')
            self.ax.set_ylabel('Z')
            self.ax.set_zlabel('Y')
            self.ax.view_init(elev=90, azim=-90)  # Adjust the viewing angle

            # Change color intensity based on y-coordinate
            for i in range(len(self.x_data) - 1):
                color_intensity = np.interp(
                    self.y_data[i], (-100, 100), (0, 1))
                self.ax.plot(self.x_data[i:i + 2],
                             self.z_data[i:i + 2],
                             self.y_data[i:i + 2],
                             color=plt.cm.Blues(color_intensity),
                             lw=2)

            self.text.set_text(
                self.text_template.format(
                    self.x_data[0],
                    self.y_data[0],
                    self.z_data[0]))

    def start_plot_graph(self):
        ani = animation.FuncAnimation(self.fig, self.update, interval=100)
        plt.show()
