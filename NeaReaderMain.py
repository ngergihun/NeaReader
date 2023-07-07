from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QComboBox, QFileDialog
import pyqtgraph as pg
import gwyfile
import sys
import numpy as np


class ImageShowWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        self.label = QLabel("Image window")
        self.graphWidget = pg.ImageView()
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.graphWidget)
        self.setLayout(layout)

        hour = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        temperature = [30, 32, 34, 32, 33, 31, 29, 32, 35, 45]

        #self.graphWidget.plot(hour, temperature)
        self.graphWidget.show()

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.channel = None
        self.image_window = None
        self.file_name = None

        layout = QVBoxLayout()
        self.load_button = QPushButton("Load Channel")
        self.show_button = QPushButton("Show")
        self.choose_file_button = QPushButton("Choose file")
        self.combo = QComboBox()
        self.combo.addItem("O3A raw")
        self.combo.addItem("O3P raw")
        self.combo.addItem("Z raw")

        self.show_button.clicked.connect(self.show_new_window)
        self.load_button.clicked.connect(self.load_gwy_channel)
        self.choose_file_button.clicked.connect(self.choose_file)

        layout.addWidget(self.choose_file_button)
        layout.addWidget(self.combo)
        layout.addWidget(self.load_button)
        layout.addWidget(self.show_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def show_new_window(self):
        if self.image_window is None:
            self.image_window = ImageShowWindow()
            self.image_window.show()
            self.image_window.graphWidget.setImage(self.channel.data)
        else:
            self.image_window.graphWidget.setImage(self.channel.data)

    def choose_file(self):
        fname = QFileDialog.getOpenFileName(self, "Choose GWY file","","Gwyddion files (*.gwy)")
        self.file_name = fname[0]
    def load_gwy_channel(self):
        #obj = gwyfile.load('2022-04-09 123828 PH PLT-EV-niceplace_spectrum_1665_cm-1.gwy')
        obj = gwyfile.load(self.file_name)
        channels = gwyfile.util.get_datafields(obj)
        channel_name = self.combo.currentText()
        self.channel = channels[channel_name]
        print(np.size(self.channel.data))

app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()