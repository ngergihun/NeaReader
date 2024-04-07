import sys
from PySide6.QtWidgets import QApplication, QFileDialog, QTreeWidgetItem, QLabel, QVBoxLayout, QWidget, QProgressBar, QMessageBox
from PySide6.QtGui import QTransform, QFont
from PySide6.QtCore import Qt, Signal, Slot, QFileInfo
import pyqtgraph as pg
import numpy as np
import random
import os
sys.path.append(os.getcwd())
import NeaImager as neaim
import copy
import matplotlib.pyplot as plt
# from qt_material import apply_stylesheet

current_folder = os.getcwd()
ui_file = os.path.join(current_folder,'App\\HyperImager.ui')
example_file = os.path.join(current_folder,'Examples\\testPsHetImage.gwy')

uiclass, baseclass = pg.Qt.loadUiType(ui_file)

class MainWindow(uiclass, baseclass):
    meas_loaded = Signal()
    def __init__(self):
        super().__init__()
        # Load UI
        self.setupUi(self)
        self.plotMenuContainer.setHidden(True)
        # Add other UI elements
        self.channelcombobox.addItems(['O0A raw', 'O0P raw', 'O1A raw', 'O1P raw', 'O2A raw', 'O2P raw', 'O3A raw', 'O3P raw',
                             'O4A raw', 'O4P raw', 'O5A raw', 'O5P raw', 'Z raw', 'Z C', 'M0A raw', 'M0P raw',
                             'M1A raw', 'M1P raw', ])
        self.channelcombobox.setCurrentIndex(4)
        self.measinfo_treeWidget.setColumnCount(2)
        self.measinfo_treeWidget.setHeaderLabels(["Property", "Value"])
        self.nextButton.setText("\U0001F87A")
        self.prevButton.setText("\U0001F878")
        self.linelevelComboBox.addItems(['Mean','Median','Median of differences'])
        self.selfRefcomboBox.addItems(['1','2','3','4','5'])
        self.colorbarcomboBox.addItems(['CET-L1','CET-L3','inferno','CET-D1','CET-D1A','CET-D3'])
        # setup stylesheet
        # apply_stylesheet(app, theme='light_blue.xml', invert_secondary=True)

        # Additional arguments and properties
        self.measurement = neaim.NeaImage()
        self.correctedMeasList = []
        self.current_file_name = None
        self.colorMapName = 'CET-D3'
        self.plane_rois = []

        # Assign function to buttons
        self.openfile.clicked.connect(self.choose_file)
        self.loadchannel.clicked.connect(self.load_meas)
        self.load_info.clicked.connect(self.choose_info_file)
        self.ApplyCorrectionButton.clicked.connect(self.ApplySingleCorrection)
        self.fileButton.toggled.connect(lambda: self.LeftMenuStack.setCurrentIndex(0))
        self.saveButton.toggled.connect(lambda: self.LeftMenuStack.setCurrentIndex(1))
        self.colorbarcomboBox.currentTextChanged.connect(self.colormapChanged)
        self.resetcolorbarButton.clicked.connect(lambda: self.update_image(self.measurement))
        self.DrawROIs_button.clicked.connect(self.putPlaneROIs)
        self.CancelROIs_button.clicked.connect(self.removePlaneROIs)
        self.meas_loaded.connect(self.updateHeaderLabel)

        # Create default plot
        self.current_file_name = example_file
        self.measurement.filename = example_file
        # CREATE AND CUSTOMIZE PLOT WIDGET
        pg.setConfigOptions(imageAxisOrder='row-major')                                 #TODO: check if this is needed
        self.imItem = pg.ImageItem()                                                    # create an ImageItem
        self.plotContainer.addItem(self.imItem)                                                             # add it to the PlotWidget
        self.cbar = self.plotContainer.addColorBar(self.imItem,colorMap=self.colorMapName,rounding=0.001)   # Create a colorBarItem and add to the PlotWidget
        self.cbar.sigLevelsChanged.connect(self.updateCbarSpinboxes)
        self.plotContainer.setBackground('w')
        axPen = pg.mkPen(color=(23, 54, 93), style=Qt.SolidLine, width = 1)
        axFont = QFont()
        axFont.setPointSize(12)
        axList = ['bottom','left','top','right']
        for ax in axList:
            self.plotContainer.getAxis(ax).setPen(axPen)
            self.plotContainer.getAxis(ax).setTextPen(axPen)
            self.plotContainer.getAxis(ax).label.setFont(axFont)
            if ax == 'top' or ax == 'right':
                 self.plotContainer.getAxis(ax).setStyle(tickFont=axFont, tickLength = 0)
            else:
                 self.plotContainer.getAxis(ax).setStyle(tickFont=axFont, tickLength = 5)

        self.plotContainer.getAxis('bottom').setLabel('X position / μm')
        self.plotContainer.getAxis('left').setLabel('Y position / μm')
        self.plotContainer.showAxes(True)
        self.plotContainer.setAspectLocked(True)
        self.plotContainer.setMouseTracking(True)
        self.imItem.hoverEvent = self.imageHoverEvent        # Attach event
        # Add on overlay image for further use
        self.imItem_overlay = pg.ImageItem()
        self.plotContainer.addItem(self.imItem_overlay)
        # Load the example measurement
        self.load_meas()

    def imageHoverEvent(self,event):
        # Show the position, pixel, and value under the mouse cursor.
        if event.isExit():
            self.plotContainer.setTitle("")
            return
        pos = event.pos()
        i, j = pos.y(), pos.x()
        i = int(np.clip(i, 0, self.imItem.image.shape[0] - 1))
        j = int(np.clip(j, 0, self.imItem.image.shape[1] - 1))
        val = self.imItem.image[i, j]
        # val = self.measurement.data[i, j]
        ppos = self.imItem.mapToParent(pos)
        x, y = ppos.x(), ppos.y()
        self.plotContainer.setTitle("pos: (%0.1f, %0.1f)  pixel: (%d, %d)  value: %.3g" % (x, y, i, j, val))

    def choose_file(self):
            fname = QFileDialog.getOpenFileName(self, "Choose GWY file","","Gwyddion files (*.gwy)")
            self.current_file_name = fname[0]
            self.measurement.filename = fname[0]

    def choose_info_file(self):
            if self.measurement is not None:
                fname = QFileDialog.getOpenFileName(self, "Choose NeaSpec info file","","Text files (*.txt)")
                self.measurement.parameters = self.measurement.read_info_file(fname[0])
                self.tree_from_dict(data=self.measurement.parameters,parent=self.measinfo_treeWidget)
            else:
                pass #TODO: Error pop-up window

    def load_meas(self):
            channelname = self.channelcombobox.currentText()
            self.measurement.read_from_gwyfile(self.current_file_name,channelname)
            finfo = QFileInfo(self.measurement.filename)
            self.measurement.meas_name = str(finfo.fileName())
            self.correctedMeasList = [self.measurement]
            print(f'Amp: {self.measurement.isamp}, Phase: {self.measurement.isphase}, Topo: {self.measurement.istopo}')
            if self.measurement.istopo:
                 self.colorMapName = 'CET-L1'
            elif self.measurement.isphase:
                self.colorMapName = 'CET-D1A'
            elif self.measurement.isamp:
                 self.colorMapName = 'CET-L3'
            else:
                 self.colorMapName = 'CET-D3'

            self.update_image(self.measurement)
            print(np.shape(self.measurement.data),'datapoints were loaded')
            self.meas_loaded.emit()

    def update_image(self,m):
        self.imItem.setImage(image = m.data)
        self.cbar.setColorMap(pg.colormap.get(self.colorMapName))
        if not self.cBcheckBox.isChecked():
            self.cbar.setLevels(values = (self.minCb.value(),self.maxCb.value()))
        else:
            self.cbar.setLevels(values = (np.min(m.data),np.max(m.data)))
            self.minCb.setValue(np.min(m.data))
            self.maxCb.setValue(np.max(m.data))
        # tr = QTransform()                                   # TODO: prepare ImageItem transformation
        # tr.scale(m.xreal*1000, m.yreal*1000)                # scale horizontal and vertical axes
        # self.imItem.setTransform(tr)

    def updateCbarSpinboxes(self):
        v = self.cbar.levels()
        self.minCb.setValue(v[0])
        self.maxCb.setValue(v[1])

    def colormapChanged(self,value):
        self.colorMapName = value
        self.update_image(self.measurement)

    def updateHeaderLabel(self):
         self.headerLabel.setText(f'{self.measurement.meas_name} - {self.measurement.channel_name}')

    def ApplySingleCorrection(self):
         methodidx = self.correctionsToolBox.currentIndex()
         match methodidx:
            case 0:
                self.levelTheLines()
            case 1:
                self.fitTheBackground()
            case 2:
                m_roibg, f_roibg = self.PlaneROIFit()
                self.correctedMeasList.append(m_roibg)
                self.measurement = self.correctedMeasList[-1]
                self.update_image(self.measurement)
                self.removePlaneROIs()
            case 3:
                self.rotateThePhase()
            case 4:
                self.selfReferencing()

    def levelTheLines(self):
        choosen_type = self.linelevelComboBox.currentText()
        match choosen_type:
            case 'Median':
                  mtype = 'median'
            case 'Mean':
                  mtype = 'average'
            case 'Median of differences':
                  mtype = 'difference'
        m_levelled = neaim.LineLevel(inputobj = self.measurement, mtype = mtype)
        self.correctedMeasList.append(m_levelled)
        self.measurement = self.correctedMeasList[-1]
        self.update_image(self.measurement)

    def fitTheBackground(self):
        xdegree = self.bgDegreeXspinBox.value()
        ydegree = self.bgDegreeYspinBox.value()
        m_bg,f_bg = neaim.BackgroundPolyFit(inputobj = self.correctedMeasList[-1], xorder=ydegree, yorder=xdegree) # x and y is switched because of row-major axis settings
        self.correctedMeasList.append(m_bg)
        self.measurement = self.correctedMeasList[-1]
        self.update_image(self.measurement)

    def rotateThePhase(self):
        alpha = self.phaseRotSpinBox.value()
        m_rot = neaim.RotatePhase(inputobj = self.correctedMeasList[-1], degree = alpha)
        self.correctedMeasList.append(m_rot)
        self.measurement = self.correctedMeasList[-1]
        self.update_image(self.measurement)

    def selfReferencing(self):
        order = int(self.selfRefcomboBox.currentText())
        m_ref = neaim.SelfReferencing(inputobj = self.correctedMeasList[-1], order = order)
        self.correctedMeasList.append(m_ref)
        self.measurement = self.correctedMeasList[-1]
        self.update_image(self.measurement)

    def putPlaneROIs(self):
        roi_radius = 5
        while len(self.plane_rois) < 3:
            posx = random.randint(roi_radius, self.measurement.xres-roi_radius-1)
            posy = random.randint(roi_radius, self.measurement.yres-roi_radius-1)
            self.plane_rois.append(pg.CircleROI([posx, posy], radius=roi_radius, translateSnap=True, rotatable=False, scaleSnap=True, ))
            self.plotContainer.addItem(self.plane_rois[-1])
            self.plane_rois[-1].sigRegionChanged.connect(self.updatePlaneRoi)
        self.updatePlaneRoi()

    def removePlaneROIs(self):
        while not len(self.plane_rois) == 0:
            self.plane_rois[-1].sigRegionChanged.disconnect(self.updatePlaneRoi)
            self.plotContainer.removeItem(self.plane_rois[-1])
            self.plane_rois = self.plane_rois[0:-1]
        self.overlay = np.zeros(np.shape(self.imItem.image))
        self.imItem_overlay.setImage(image = self.overlay)
        self.imItem_overlay.setOpts(opacity = 0)

    def updatePlaneRoi(self):
        self.xfiltered = []
        self.yfiltered = []
        self.dfiltered = []
        self.overlay = np.zeros(np.shape(self.imItem.image))

        for roi in self.plane_rois:
            datacut, coords = roi.getArrayRegion(self.imItem.image, img=self.imItem, returnMappedCoords=True)
            print(f'Shape of datacut: {np.shape(datacut)}, shape of coords: {np.shape(coords)}')

            # Separate coordinates and data array and flatten them
            Xcoords = coords[1,:,:]
            Ycoords = coords[0,:,:] # if axis set is row-major
            x, y = Xcoords.ravel(), Ycoords.ravel()
            d = datacut.ravel()

            for idx, dval in enumerate(d):
                if not dval == 0.:
                    self.overlay[int(y[idx]),int(x[idx])] = 1
                    self.yfiltered.append(int(y[idx]))
                    self.xfiltered.append(int(x[idx]))
                    self.dfiltered.append(int(d[idx]))
                else:
                    pass

        self.imItem_overlay.setImage(image = self.overlay)
        self.imItem_overlay.setOpts(opacity = 0.5)
        print(f'Length of X pos: {len(self.xfiltered)}, Length of Y pos: {len(self.yfiltered)}, Length of Data: {len(self.dfiltered)}')

    def PlaneROIFit(self):
        outputobj = copy.deepcopy(self.correctedMeasList[-1])
        Z = copy.deepcopy(outputobj.data)
        xfull = list(range(0, outputobj.xres))
        yfull = list(range(0, outputobj.yres))
        X, Y = np.meshgrid(xfull,yfull)

        def get_basis(x, y, max_order_x=1, max_order_y=1):
            """Return the fit basis polynomials: 1, x, x^2, ..., xy, x^2y, ... etc."""
            basis = []
            for i in range(max_order_y+1):
                for j in range(max_order_x - i +1):
                # for j in range(max_order_x+1):
                    basis.append(x**j * y**i)
            return basis

        xf = np.array(self.xfiltered)
        yf = np.array(self.yfiltered)
        basis = get_basis(xf, yf, 1, 1)
        A = np.vstack(basis).T
        b = np.array(self.dfiltered)
        c, r, rank, s = np.linalg.lstsq(A, b, rcond=None)

        background = np.sum(c[:, None, None] * np.array(get_basis(X, Y, 1, 1)).reshape(len(basis), *X.shape), axis=0)

        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        ax.plot_surface(X, Y, background, cmap='viridis')
        ax.scatter(self.xfiltered,self.yfiltered,b)
        plt.show()

        if outputobj.isamp:
            outputobj.data = (10*Z)/background
        else:
            outputobj.data = Z-background

        return outputobj, background

    # UI function staff
    def tree_from_dict(self, data=None, parent=None):
        self.measinfo_treeWidget.clear()
        for key, value in data.items():
            item = QTreeWidgetItem(parent)
            item.setText(0, key)
            item.setText(1, str(value))
    
    def nextCorrectionPage(self):
        self.CorrectionsQStack.setCurrentIndex(self.CorrectionsQStack.currentIndex() + 1)

    def prevCorrectionPage(self):
        self.CorrectionsQStack.setCurrentIndex(self.CorrectionsQStack.currentIndex() - 1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())