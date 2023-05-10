import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

class PlotGraph:
    def __init__(self, positioning_system):
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
        x, y, z = self.positioning_system.position
        if None not in (x, y, z):
            self.x_data.append(x)
            self.y_data.append(y)
            self.z_data.append(z)
            self.ax.clear()
            self.ax.set_xlim(-100, 100)
            self.ax.set_ylim(-100, 100)
            self.ax.set_zlim(-100, 100)
            self.ax.set_xlabel('X')
            self.ax.set_ylabel('Z')
            self.ax.set_zlabel('Y')
            self.ax.view_init(elev=90, azim=-90)  # Adjust the viewing angle

            # Change color intensity based on y-coordinate
            for i in range(len(self.x_data)-1):
                color_intensity = np.interp(self.y_data[i], (-100, 100), (0, 1))
                self.ax.plot(self.x_data[i:i+2], self.z_data[i:i+2], self.y_data[i:i+2], color=plt.cm.Blues(color_intensity), lw=2)
            
            self.text.set_text(self.text_template.format(x, y, z))

    def start_plot_graph(self):
        ani = animation.FuncAnimation(self.fig, self.update, interval=100)
        plt.show()


