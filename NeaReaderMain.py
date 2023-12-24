from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QComboBox, QFileDialog
import pyqtgraph as pg
import gwyfile
import sys
import numpy as np
import NeaImager as neaim


class ImageShowWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        self.label = QLabel("Image window")
        self.setMinimumSize(800, 600) 
        self.graphWidget = pg.ImageView()
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.graphWidget)
        self.setLayout(layout)
        self.graphWidget.show()

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.measurement = neaim.NeaImage()
        self.image_window = None
        self.current_file_name = None

        layout = QVBoxLayout()
        self.load_button = QPushButton("Load Channel")
        self.show_button = QPushButton("Show")
        self.choose_file_button = QPushButton("Choose file")
        self.align_row_button = QPushButton("Align rows")
        self.combo = QComboBox()
        self.combo.addItems(['O0A raw', 'O0P raw', 'O1A raw', 'O1P raw', 'O2A raw', 'O2P raw', 'O3A raw', 'O3P raw',
                             'O4A raw', 'O4P raw', 'O5A raw', 'O5P raw', 'Z raw', 'Z C', 'M0A raw', 'M0P raw',
                             'M1A raw', 'M1P raw', ])
        self.line_level_combo = QComboBox()
        self.line_level_combo.addItems(['median','average','difference'])

        self.show_button.clicked.connect(self.show_new_window)
        self.load_button.clicked.connect(self.load_meas)
        self.choose_file_button.clicked.connect(self.choose_file)
        self.align_row_button.clicked.connect(self.align_rows)

        layout.addWidget(self.choose_file_button)
        layout.addWidget(self.combo)
        layout.addWidget(self.load_button)
        layout.addWidget(self.show_button)
        layout.addWidget(self.line_level_combo)
        layout.addWidget(self.align_row_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def show_new_window(self):
        if self.image_window is None:
            self.image_window = ImageShowWindow()
            self.image_window.show()
            self.image_window.graphWidget.setImage(self.measurement.data)
        else:
            self.image_window.graphWidget.setImage(self.measurement.data)

    def choose_file(self):
        fname = QFileDialog.getOpenFileName(self, "Choose GWY file","","Gwyddion files (*.gwy)")
        self.current_file_name = fname[0]
        self.measurement.filename = fname[0]

    def choose_info_file(self):
        if self.measurement is not None:
            fname = QFileDialog.getOpenFileName(self, "Choose NeaSpec info file","","Text files (*.txt)")
            self.measurement.parameters = self.measurement.read_info_file(fname[0])
        else:
            pass #TODO: Error pop-up window

    def load_meas(self):
        self.measurement.channel_name = self.combo.currentText()
        self.measurement.read_from_gwyfile()
        print(np.shape(self.measurement.data),'datapoints were loaded')

    def align_rows(self, type):
        type = self.line_level_combo.currentText()
        neaim.LineLevel(inputobj = self.measurement, type = type)
        self.image_window.graphWidget.setImage(self.measurement.data)

app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()