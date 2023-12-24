import sys
from PySide6.QtWidgets import QApplication, QToolBox, QWidget, QPushButton, QVBoxLayout

app = QApplication(sys.argv)

# Create a window
window = QWidget()
window.setWindowTitle("PySide6 QToolBox Example")

# Create a QToolBox widget
toolbox = QToolBox()

# Create two sections with push buttons
section1 = QWidget()
button1 = QPushButton("Button 1")
layout1 = QVBoxLayout()
layout1.addWidget(button1)
section1.setLayout(layout1)

section2 = QWidget()
button2 = QPushButton("Button 2")
layout2 = QVBoxLayout()
layout2.addWidget(button2)
section2.setLayout(layout2)

# Add the sections to the QToolBox
toolbox.addItem(section1, "Section 1")
toolbox.addItem(section2, "Section 2")

# Set the QToolBox as the main layout of the window
window.setLayout(toolbox)

# Show the window
window.show()

# Run the application
sys.exit(app.exec_())
