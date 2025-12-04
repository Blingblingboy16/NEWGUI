import sys
import random
import time
import csv
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QWidget,
    QVBoxLayout, QInputDialog, QTableWidget, QTableWidgetItem, QDialog
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class GraphCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)


def smooth(data, window=3):
    """ Simple moving-average smoothing """
    if len(data) < window:
        return data[:]  # not enough points to smooth
    smoothed = []
    for i in range(len(data)):
        start = max(0, i - window + 1)
        smoothed.append(sum(data[start:i+1]) / (i - start + 1))
    return smoothed


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Ask the user to name the graph
        graph_name, ok = QInputDialog.getText(
            self, "Graph Name", "Enter a name for your graph:"
        )
        if not ok or graph_name.strip() == "":
            graph_name = "Plant Growth"

        self.graph_name = graph_name
        self.setWindowTitle(graph_name)

        # Store experiment data
        self.start_time = time.time()
        self.times = []
        self.lengths = []

        # CSV file name
        self.csv_filename = f"experiment_data_{graph_name.replace(' ', '_')}.csv"

        # Create CSV header
        with open(self.csv_filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Time (minutes)", "Plant Length (cm)"])

        # --- UI ---
        layout = QVBoxLayout()

        self.button = QPushButton("Add Data")
        self.button.clicked.connect(self.add_data)

        self.table_button = QPushButton("View Data Table")
        self.table_button.clicked.connect(self.view_table)

        self.graph = GraphCanvas(self)

        layout.addWidget(self.button)
        layout.addWidget(self.table_button)
        layout.addWidget(self.graph)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def add_data(self):
        # Ask user for plant length
        length, ok = QInputDialog.getDouble(
            self, "Plant Length", "Enter plant length (cm):", min=0
        )
        if not ok:
            return

        # Time since start in minutes, rounded neatly
        elapsed_minutes = round((time.time() - self.start_time) / 60, 2)

        # Store new data
        self.times.append(elapsed_minutes)
        self.lengths.append(length)

        # Save data to CSV
        with open(self.csv_filename, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([elapsed_minutes, length])

        # Smooth the curve
        smoothed_lengths = smooth(self.lengths, window=3)

        # Update graph
        self.graph.ax.clear()
        self.graph.ax.plot(self.times, smoothed_lengths, marker="o")
        self.graph.ax.set_xlabel("Time Since Start (minutes)")
        self.graph.ax.set_ylabel("Plant Length (cm)")
        self.graph.ax.set_title(self.graph_name)
        self.graph.draw()

    def view_table(self):
        """Opens a popup window showing all collected data."""

        dialog = QDialog(self)
        dialog.setWindowTitle("Data Table")
        layout = QVBoxLayout()

        table = QTableWidget()
        table.setRowCount(len(self.times))
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Time (minutes)", "Length (cm)"])

        for row, (t, l) in enumerate(zip(self.times, self.lengths)):
            table.setItem(row, 0, QTableWidgetItem(str(t)))
            table.setItem(row, 1, QTableWidgetItem(str(l)))

        layout.addWidget(table)
        dialog.setLayout(layout)
        dialog.resize(300, 400)
        dialog.exec()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())