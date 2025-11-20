import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class GraphCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Experiment Grapher")

        # --- UI ---
        layout = QVBoxLayout()

        self.button = QPushButton("Run Experiment")
        self.button.clicked.connect(self.run_experiment)

        self.graph = GraphCanvas(self)

        layout.addWidget(self.button)
        layout.addWidget(self.graph)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def run_experiment(self):
        # Simulate experiment data collection
        data_x = list(range(50))
        data_y = [random.randint(0, 20) for _ in data_x]

        # Plot the data
        self.graph.ax.clear()
        self.graph.ax.plot(data_x, data_y)
        self.graph.ax.set_title("Experiment Results")
        self.graph.draw()   # refresh canvas


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
