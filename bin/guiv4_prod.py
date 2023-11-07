#!/dls/science/groups/i23/pyenvs/aithreconda/bin/python

# C Orr 2022
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
import cv2 as cv
from control import ca
import pv
import math
import sys
import numpy as np
import time

# Set beam position and scale.
line_width = 1
line_spacing = 60
line_color = (164, 164, 164)
beamX = 1155
beamY = 718
# div 2 if using Qt gui as its half size


# pixel size 3.45, 2 to 1 imaging system so calib 1/2
calibrate = 0.00172
# calibrate = 0.00345

# separate thread for OAV
class OAVThread(QThread):
    ImageUpdate = pyqtSignal(QImage)
    zoom = 1

    def updateZoom(self, zoom):
        self.zoom = zoom

    def run(self):
        self.ThreadActive = True
        cap = cv.VideoCapture("http://bl23i-ea-serv-01.diamond.ac.uk:8080/OAV.mjpg.mjpg")
        while self.ThreadActive:
            ret, frame = cap.read()
            if self.ThreadActive:
                for i in range(14, frame.shape[1], line_spacing):
                    cv.line(frame, (i, 0), (i, frame.shape[0]), line_color, line_width)
                for i in range(beamY % line_spacing, frame.shape[0], line_spacing):
                    cv.line(frame, (0, i), (frame.shape[1], i), line_color, line_width)
                
                cv.line(
                    frame,
                    (beamX - 10, beamY),
                    (beamX + 10, beamY),
                    (0, 255, 0),
                    2,
                )
                cv.line(
                    frame,
                    (beamX, beamY - 10),
                    (beamX, beamY + 10),
                    (0, 255, 0),
                    2,
                )
               # cv.ellipse(frame, (beamX, beamY), (12, 8), 0.0, 0.0, 360, (0,0,255), thickness=2) # could use to draw cut...
                # cv.putText(frame,'text',bottomLeftCornerOfText, font, fontScale, fontColor, thickness, lineType)
                rgbImage = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                convertToQtFormat = QtGui.QImage(
                    rgbImage.data,
                    rgbImage.shape[1],
                    rgbImage.shape[0],
                    QtGui.QImage.Format_RGB888,
                )
                # if self.zoom == 2:
                #     convertToQtFormat = convertToQtFormat[258:(258 + 979), 428:(428 + 1302)]
                # else:
                #     pass
                p = convertToQtFormat
                p = convertToQtFormat.scaled(1032, 772, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(p)

    def stop(self):
        self.ThreadActive = False
        self.quit()
        
# class BLSThread(QThread):
#     safe = pyqtSignal(bool)

#     def run(self):
#         self.ThreadActive = True
#         while self.ThreadActive:
#             time.sleep(5)
#             for rbv in [pv.omega_rbv, pv.gonio_y_rbv, pv.gonio_z_rbv, pv.stage_x_rbv, pv.stage_y_rbv]: 
#                 if round(float(ca.caget(rbv)), 1) == 0.0:
#                     safe = True
#             self.safe.emit(safe)

# separate thread to run caget for RBVs
class RBVThread(QThread):
    rbvUpdate = pyqtSignal(list)

    def run(self):
        self.ThreadActive = True
        while self.ThreadActive:
            time.sleep(0.5)
            allRBVsList = []
            allRBVsList += [str(ca.caget(pv.stage_z_rbv))]
            allRBVsList += [str(ca.caget(pv.gonio_y_rbv))]
            allRBVsList += [str(ca.caget(pv.gonio_z_rbv))]
            allRBVsList += [str(ca.caget(pv.omega_rbv))]
            allRBVsList += [str(ca.caget(pv.oav_cam_acqtime_rbv))]
            allRBVsList += [str(ca.caget(pv.oav_cam_gain_rbv))]
            allRBVsList += [str(ca.caget(pv.robot_current_pin_rbv))]
            if (
                ca.caget(pv.robot_pin_mounted) is True
            ):  # need to work out what this pv returns
                allRBVsList += "\u2714"
            elif ca.caget(pv.robot_pin_mounted) is False:
                allRBVsList += "\u274C"
            else:
                allRBVsList += "\u003F"
            allRBVsList += [str(ca.caget(pv.stage_x_rbv))]
            allRBVsList += [str(ca.caget(pv.stage_y_rbv))]
            self.rbvUpdate.emit(allRBVsList)
            allRBVsList = []


# not working yet. Kind of. Ish. Need to have it emit to gui
# class Worker3(QThread):
#     def run(self):
#         self.ThreadActive = True
#         cap = cv.VideoCapture("http://ws464.diamond.ac.uk:8080/OAV.mjpg.mjpg")
#         while self.ThreadActive:
#             cv.namedWindow("RoboView")
#             ret, frame = cap.read()
#             if self.ThreadActive:
#                 cv.imshow("RoboView", frame)

#     def stop(self):
#         self.ThreadActive = False
#         cap = cv.VideoCapture("http://i23-lasereye-01.diamond.ac.uk/mjpg/video.mjpg")
#         cap.release()


class Ui_MainWindow(object):
    def __init__(self):
        super().__init__()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1088, 874)
        MainWindow.setMinimumSize(QtCore.QSize(0, 0))
        MainWindow.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setPointSize(12)
        MainWindow.setFont(font)
        MainWindow.setMouseTracking(False)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setToolTip("")
        MainWindow.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        MainWindow.setDocumentMode(False)
        MainWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
        MainWindow.setUnifiedTitleAndToolBarOnMac(False)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.frameFineControl = QtWidgets.QFrame(self.centralwidget)
        self.frameFineControl.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameFineControl.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frameFineControl.setObjectName("frameFineControl")
        self.readback_grid = QtWidgets.QGridLayout(self.frameFineControl)
        self.readback_grid.setObjectName("readback_grid")
        self.exposure_rbv = QtWidgets.QLabel(self.frameFineControl)
        self.exposure_rbv.setObjectName("exposure_rbv")
        self.readback_grid.addWidget(self.exposure_rbv, 1, 1, 1, 1)
        self.labZ = QtWidgets.QLabel(self.frameFineControl)
        self.labZ.setAlignment(QtCore.Qt.AlignCenter)
        self.labZ.setObjectName("labZ")
        self.readback_grid.addWidget(self.labZ, 5, 0, 1, 1)
        self.gain_rbv = QtWidgets.QLabel(self.frameFineControl)
        self.gain_rbv.setObjectName("gain_rbv")
        self.readback_grid.addWidget(self.gain_rbv, 2, 1, 1, 1)
        self.gony_rbv = QtWidgets.QLabel(self.frameFineControl)
        self.gony_rbv.setObjectName("gony_rbv")
        self.readback_grid.addWidget(self.gony_rbv, 4, 1, 1, 1)
        self.gony_request = QtWidgets.QLineEdit(self.frameFineControl)
        self.gony_request.setMaxLength(5)
        self.gony_request.setObjectName("gony_request")
        self.readback_grid.addWidget(self.gony_request, 4, 3, 1, 1)
        self.labZoom = QtWidgets.QLabel(self.frameFineControl)
        self.labZoom.setObjectName("labZoom")
        self.readback_grid.addWidget(self.labZoom, 0, 0, 1, 1)
        self.labGain = QtWidgets.QLabel(self.frameFineControl)
        self.labGain.setObjectName("labGain")
        self.readback_grid.addWidget(self.labGain, 2, 0, 1, 1)
        self.gonz_request = QtWidgets.QLineEdit(self.frameFineControl)
        self.gonz_request.setMaxLength(5)
        self.gonz_request.setObjectName("gonz_request")
        self.readback_grid.addWidget(self.gonz_request, 5, 3, 1, 1)
        self.stagez_rbv = QtWidgets.QLabel(self.frameFineControl)
        self.stagez_rbv.setObjectName("stagez_rbv")
        self.readback_grid.addWidget(self.stagez_rbv, 3, 1, 1, 1)
        self.labExposure = QtWidgets.QLabel(self.frameFineControl)
        self.labExposure.setObjectName("labExposure")
        self.readback_grid.addWidget(self.labExposure, 1, 0, 1, 1)
        self.sliderGain = QtWidgets.QSlider(self.frameFineControl)
        self.sliderGain.setMaximum(100)
        self.sliderGain.setOrientation(QtCore.Qt.Horizontal)
        self.sliderGain.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        self.sliderGain.setTickInterval(5)
        self.sliderGain.setObjectName("sliderGain")
        self.readback_grid.addWidget(self.sliderGain, 2, 3, 1, 1)
        self.sliderExposure = QtWidgets.QSlider(self.frameFineControl)
        self.sliderExposure.setMinimum(1)
        self.sliderExposure.setMaximum(100)
        # self.sliderExposure.setProperty("value", 1)
        self.sliderExposure.setOrientation(QtCore.Qt.Horizontal)
        self.sliderExposure.setInvertedAppearance(False)
        self.sliderExposure.setInvertedControls(False)
        self.sliderExposure.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        self.sliderExposure.setTickInterval(5)
        self.sliderExposure.setObjectName("sliderExposure")
        self.readback_grid.addWidget(self.sliderExposure, 1, 3, 1, 1)
        self.zoomSelect = QtWidgets.QComboBox(self.frameFineControl)
        self.zoomSelect.setInsertPolicy(QtWidgets.QComboBox.InsertAtBottom)
        self.zoomSelect.setObjectName("zoomSelect")
        self.zoomSelect.addItem("")
        self.zoomSelect.addItem("")
        self.zoomSelect.addItem("")
        self.zoomSelect.addItem("")
        self.readback_grid.addWidget(self.zoomSelect, 0, 3, 1, 1)
        self.omega_request = QtWidgets.QLineEdit(self.frameFineControl)
        self.omega_request.setMaxLength(5)
        self.omega_request.setObjectName("omega_request")
        self.readback_grid.addWidget(self.omega_request, 7, 3, 1, 1)
        self.stagez_request = QtWidgets.QLineEdit(self.frameFineControl)
        self.stagez_request.setText("")
        self.stagez_request.setMaxLength(5)
        self.stagez_request.setObjectName("stagez_request")
        self.readback_grid.addWidget(self.stagez_request, 3, 3, 1, 1)
        self.gonz_rbv = QtWidgets.QLabel(self.frameFineControl)
        self.gonz_rbv.setObjectName("gonz_rbv")
        self.readback_grid.addWidget(self.gonz_rbv, 5, 1, 1, 1)
        self.omega_rbv = QtWidgets.QLabel(self.frameFineControl)
        self.omega_rbv.setObjectName("omega_rbv")
        self.readback_grid.addWidget(self.omega_rbv, 7, 1, 1, 1)
        self.labOmega = QtWidgets.QLabel(self.frameFineControl)
        self.labOmega.setAlignment(QtCore.Qt.AlignCenter)
        self.labOmega.setObjectName("labOmega")
        self.readback_grid.addWidget(self.labOmega, 7, 0, 1, 1)
        self.labX = QtWidgets.QLabel(self.frameFineControl)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labX.sizePolicy().hasHeightForWidth())
        self.labX.setSizePolicy(sizePolicy)
        self.labX.setAlignment(QtCore.Qt.AlignCenter)
        self.labX.setObjectName("labX")
        self.readback_grid.addWidget(self.labX, 3, 0, 1, 1)
        self.labY = QtWidgets.QLabel(self.frameFineControl)
        self.labY.setAlignment(QtCore.Qt.AlignCenter)
        self.labY.setObjectName("labY")
        self.readback_grid.addWidget(self.labY, 4, 0, 1, 1)
        self.gridLayout.addWidget(self.frameFineControl, 2, 2, 1, 1)
        self.start = QtWidgets.QPushButton(self.centralwidget)
        self.start.setObjectName("start")
        self.gridLayout.addWidget(self.start, 1, 0, 1, 1)
        self.stop = QtWidgets.QPushButton(self.centralwidget)
        self.stop.setObjectName("stop")
        self.gridLayout.addWidget(self.stop, 1, 2, 1, 1)
        self.snapshot = QtWidgets.QPushButton(self.centralwidget)
        self.snapshot.setObjectName("snapshot")
        self.gridLayout.addWidget(self.snapshot, 1, 4, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
        )
        self.gridLayout.addItem(spacerItem, 2, 3, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
        )
        self.gridLayout.addItem(spacerItem1, 2, 1, 1, 1)
        self.oav_stream = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.oav_stream.sizePolicy().hasHeightForWidth())
        self.oav_stream.setSizePolicy(sizePolicy)
        self.oav_stream.setText("")
        self.oav_stream.setPixmap(QtGui.QPixmap("icon.png"))
        self.oav_stream.setScaledContents(True)
        self.oav_stream.setAlignment(QtCore.Qt.AlignCenter)
        self.oav_stream.setObjectName("oav_stream")
        self.gridLayout.addWidget(self.oav_stream, 0, 0, 1, 5)
        self.framePositionButtons = QtWidgets.QFrame(self.centralwidget)
        self.framePositionButtons.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.framePositionButtons.setFrameShadow(QtWidgets.QFrame.Plain)
        self.framePositionButtons.setObjectName("framePositionButtons")
        self.motion_grid = QtWidgets.QGridLayout(self.framePositionButtons)
        self.motion_grid.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.motion_grid.setSpacing(5)
        self.motion_grid.setObjectName("motion_grid")
        self.up = QtWidgets.QPushButton(self.framePositionButtons)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.up.sizePolicy().hasHeightForWidth())
        self.up.setSizePolicy(sizePolicy)
        self.up.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("up.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.up.setIcon(icon1)
        self.up.setIconSize(QtCore.QSize(60, 60))
        self.up.setObjectName("up")
        self.motion_grid.addWidget(self.up, 0, 1, 1, 1)
        self.minus90 = QtWidgets.QPushButton(self.framePositionButtons)
        self.minus90.setObjectName("minus90")
        self.motion_grid.addWidget(self.minus90, 3, 2, 1, 1)
        self.plus5 = QtWidgets.QPushButton(self.framePositionButtons)
        self.plus5.setObjectName("plus5")
        self.motion_grid.addWidget(self.plus5, 4, 0, 1, 1)
        self.plus90 = QtWidgets.QPushButton(self.framePositionButtons)
        self.plus90.setObjectName("plus90")
        self.motion_grid.addWidget(self.plus90, 4, 2, 1, 1)
        self.plus15 = QtWidgets.QPushButton(self.framePositionButtons)
        self.plus15.setObjectName("plus15")
        self.motion_grid.addWidget(self.plus15, 4, 1, 1, 1)
        self.down = QtWidgets.QPushButton(self.framePositionButtons)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.down.sizePolicy().hasHeightForWidth())
        self.down.setSizePolicy(sizePolicy)
        self.down.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("down.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.down.setIcon(icon2)
        self.down.setIconSize(QtCore.QSize(60, 60))
        self.down.setAutoRepeat(False)
        self.down.setAutoExclusive(False)
        self.down.setObjectName("down")
        self.motion_grid.addWidget(self.down, 2, 1, 1, 1)
        self.minus180 = QtWidgets.QPushButton(self.framePositionButtons)
        self.minus180.setObjectName("minus180")
        self.motion_grid.addWidget(self.minus180, 3, 3, 1, 1)
        self.minus5 = QtWidgets.QPushButton(self.framePositionButtons)
        self.minus5.setObjectName("minus5")
        self.motion_grid.addWidget(self.minus5, 3, 0, 1, 1)
        self.minus15 = QtWidgets.QPushButton(self.framePositionButtons)
        self.minus15.setObjectName("minus15")
        self.motion_grid.addWidget(self.minus15, 3, 1, 1, 1)
        self.plus180 = QtWidgets.QPushButton(self.framePositionButtons)
        self.plus180.setObjectName("plus180")
        self.motion_grid.addWidget(self.plus180, 4, 3, 1, 1)
        self.left = QtWidgets.QPushButton(self.framePositionButtons)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.left.sizePolicy().hasHeightForWidth())
        self.left.setSizePolicy(sizePolicy)
        self.left.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("left.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.left.setIcon(icon3)
        self.left.setIconSize(QtCore.QSize(60, 60))
        self.left.setObjectName("left")
        self.motion_grid.addWidget(self.left, 1, 0, 1, 1)
        self.right = QtWidgets.QPushButton(self.framePositionButtons)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.right.sizePolicy().hasHeightForWidth())
        self.right.setSizePolicy(sizePolicy)
        self.right.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("right.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.right.setIcon(icon4)
        self.right.setIconSize(QtCore.QSize(60, 60))
        self.right.setObjectName("right")
        self.motion_grid.addWidget(self.right, 1, 2, 1, 1)
        self.zero = QtWidgets.QPushButton(self.framePositionButtons)
        self.zero.setObjectName("zero")
        self.motion_grid.addWidget(self.zero, 2, 3, 1, 1)
        self.zeroAll = QtWidgets.QPushButton(self.framePositionButtons)
        self.zeroAll.setFlat(False)
        self.zeroAll.setObjectName("zeroAll")
        self.motion_grid.addWidget(self.zeroAll, 0, 3, 1, 1)
        self.gridLayout.addWidget(self.framePositionButtons, 2, 0, 1, 1)
        self.frameRobot = QtWidgets.QFrame(self.centralwidget)
        self.frameRobot.setAutoFillBackground(False)
        self.frameRobot.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameRobot.setObjectName("frameRobot")
        self.robot_grid = QtWidgets.QGridLayout(self.frameRobot)
        self.robot_grid.setObjectName("robot_grid")
        self.spinToLoad = QtWidgets.QSpinBox(self.frameRobot)
        self.spinToLoad.setProperty("showGroupSeparator", False)
        self.spinToLoad.setMinimum(1)
        self.spinToLoad.setMaximum(16)
        self.spinToLoad.setObjectName("spinToLoad")
        self.robot_grid.addWidget(self.spinToLoad, 3, 1, 1, 1)
        self.gonioSens = QPushButton(self.frameRobot)
        self.gonioSens.setObjectName("gonioSens")
        self.gonioSens.setMinimumSize(QSize(30, 30))
        self.gonioSens.setMaximumSize(QSize(30, 30))
        self.gonioSens.setStyleSheet("background-color: red")
        self.robot_grid.addWidget(self.gonioSens, 1, 1, 1, 1, QtCore.Qt.AlignHCenter)
        self.labGonioSens = QtWidgets.QLabel(self.frameRobot)
        self.labGonioSens.setObjectName("labGonioSens")
        self.robot_grid.addWidget(self.labGonioSens, 1, 0, 1, 1)
        self.load = QtWidgets.QPushButton(self.frameRobot)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.load.sizePolicy().hasHeightForWidth())
        self.load.setSizePolicy(sizePolicy)
        self.load.setObjectName("load")
        self.robot_grid.addWidget(self.load, 3, 0, 1, 1)
        self.currentSamp = QtWidgets.QLabel(self.frameRobot)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.currentSamp.sizePolicy().hasHeightForWidth())
        self.currentSamp.setSizePolicy(sizePolicy)
        self.currentSamp.setAutoFillBackground(False)
        self.currentSamp.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.currentSamp.setObjectName("currentSamp")
        self.robot_grid.addWidget(self.currentSamp, 0, 1, 1, 1, QtCore.Qt.AlignHCenter)
        self.labCurrentSamp = QtWidgets.QLabel(self.frameRobot)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.labCurrentSamp.sizePolicy().hasHeightForWidth()
        )
        self.labCurrentSamp.setSizePolicy(sizePolicy)
        self.labCurrentSamp.setObjectName("labCurrentSamp")
        self.robot_grid.addWidget(self.labCurrentSamp, 0, 0, 1, 1)
        self.unload = QtWidgets.QPushButton(self.frameRobot)
        self.unload.setObjectName("unload")
        self.robot_grid.addWidget(self.unload, 4, 0, 1, 1)
        self.dry = QtWidgets.QPushButton(self.frameRobot)
        self.dry.setObjectName("dry")
        self.robot_grid.addWidget(self.dry, 4, 1, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(
            20,
            40,
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.MinimumExpanding,
        )
        self.robot_grid.addItem(spacerItem2, 2, 0, 1, 2)
        self.gridLayout.addWidget(self.frameRobot, 2, 4, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1088, 24))
        self.menuBar.setObjectName("menuBar")
        self.menuFile = QtWidgets.QMenu(self.menuBar)
        self.menuFile.setObjectName("menuFile")
        self.menuIOCs = QtWidgets.QMenu(self.menuBar)
        self.menuIOCs.setObjectName("menuIOCs")
        MainWindow.setMenuBar(self.menuBar)
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionSave_log = QtWidgets.QAction(MainWindow)
        self.actionSave_log.setObjectName("actionSave_log")
        self.actionRestart_OAV_IOC = QtWidgets.QAction(MainWindow)
        self.actionRestart_OAV_IOC.setObjectName("actionRestart_OAV_IOC")
        self.actionRestart_Robot_IOC = QtWidgets.QAction(MainWindow)
        self.actionRestart_Robot_IOC.setObjectName("actionRestart_Robot_IOC")
        self.actionRestart_Gonio_IOC = QtWidgets.QAction(MainWindow)
        self.actionRestart_Gonio_IOC.setObjectName("actionRestart_Gonio_IOC")
        self.menuFile.addAction(self.actionExit)
        self.menuFile.addAction(self.actionSave_log)
        self.menuIOCs.addAction(self.actionRestart_OAV_IOC)
        self.menuIOCs.addAction(self.actionRestart_Robot_IOC)
        self.menuIOCs.addAction(self.actionRestart_Gonio_IOC)
        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuIOCs.menuAction())

        self.retranslateUi(MainWindow)
        self.zoomSelect.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.load, self.unload)
        MainWindow.setTabOrder(self.unload, self.spinToLoad)
        MainWindow.setTabOrder(self.spinToLoad, self.dry)
        MainWindow.setTabOrder(self.dry, self.start)
        MainWindow.setTabOrder(self.start, self.stop)
        MainWindow.setTabOrder(self.stop, self.sliderExposure)
        MainWindow.setTabOrder(self.sliderExposure, self.sliderGain)
        MainWindow.setTabOrder(self.sliderGain, self.stagez_request)
        MainWindow.setTabOrder(self.stagez_request, self.gony_request)
        MainWindow.setTabOrder(self.gony_request, self.gonz_request)
        MainWindow.setTabOrder(self.gonz_request, self.omega_request)
        MainWindow.setTabOrder(self.omega_request, self.up)
        MainWindow.setTabOrder(self.up, self.down)
        MainWindow.setTabOrder(self.down, self.left)
        MainWindow.setTabOrder(self.left, self.right)
        MainWindow.setTabOrder(self.right, self.minus5)
        MainWindow.setTabOrder(self.minus5, self.snapshot)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(
            _translate("MainWindow", "Aithre v4.1 - I23 Laser Shaping")
        )
        self.exposure_rbv.setText(_translate("MainWindow", "0.04"))
        self.labZ.setText(_translate("MainWindow", "Z"))
        self.gain_rbv.setText(_translate("MainWindow", "0"))
        self.gony_rbv.setText(_translate("MainWindow", "0.12"))
        self.labZoom.setText(_translate("MainWindow", "Zoom"))
        self.labGain.setText(_translate("MainWindow", "Gain"))
        self.stagez_rbv.setText(_translate("MainWindow", "0.352"))
        self.labExposure.setText(_translate("MainWindow", "Exposure"))
        self.zoomSelect.setCurrentText(_translate("MainWindow", "1"))
        self.zoomSelect.setItemText(0, _translate("MainWindow", "1"))
        self.zoomSelect.setItemText(1, _translate("MainWindow", "2"))
        self.zoomSelect.setItemText(2, _translate("MainWindow", "4"))
        self.zoomSelect.setItemText(3, _translate("MainWindow", "8"))
        self.gonz_rbv.setText(_translate("MainWindow", "0.55"))
        self.omega_rbv.setText(_translate("MainWindow", "0.00"))
        self.labOmega.setText(_translate("MainWindow", "Omega"))
        self.labX.setText(_translate("MainWindow", "X"))
        self.labY.setText(_translate("MainWindow", "Y"))
        self.start.setText(_translate("MainWindow", "Start"))
        self.stop.setText(_translate("MainWindow", "Stop"))
        self.snapshot.setText(_translate("MainWindow", "Snapshot"))
        self.minus90.setText(_translate("MainWindow", "-90"))
        self.plus5.setText(_translate("MainWindow", "+5"))
        self.plus90.setText(_translate("MainWindow", "+90"))
        self.plus15.setText(_translate("MainWindow", "+15"))
        self.minus180.setText(_translate("MainWindow", "-180"))
        self.minus5.setText(_translate("MainWindow", "-5"))
        self.minus15.setText(_translate("MainWindow", "-15"))
        self.plus180.setText(_translate("MainWindow", "+180"))
        self.zero.setText(_translate("MainWindow", "0"))
        self.zeroAll.setText(_translate("MainWindow", "ZeroAll"))
        self.labGonioSens.setText(_translate("MainWindow", "Gonio Sensor"))
        self.load.setText(_translate("MainWindow", "Load"))
        self.currentSamp.setText(_translate("MainWindow", "0"))
        self.labCurrentSamp.setText(_translate("MainWindow", "Current Sample"))
        self.unload.setText(_translate("MainWindow", "Unload"))
        self.dry.setText(_translate("MainWindow", "Dry"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuIOCs.setTitle(_translate("MainWindow", "IOCs"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionSave_log.setText(_translate("MainWindow", "Save log"))
        self.actionRestart_OAV_IOC.setText(_translate("MainWindow", "Restart OAV IOC"))
        self.actionRestart_Robot_IOC.setText(
            _translate("MainWindow", "Restart Robot IOC")
        )
        self.actionRestart_Gonio_IOC.setText(
            _translate("MainWindow", "Restart Gonio IOC")
        )
        # setup
        # menus
        self.actionExit.triggered.connect(self.quit)
        # sliders and sensors
        self.sliderExposure.setProperty(
            "value", str(round(float(ca.caget(pv.oav_cam_acqtime_rbv)) * 100))
        )
        self.sliderGain.setProperty(
            "value", str(round(float(ca.caget(pv.oav_cam_gain_rbv))))
        )
        # OAV connections thread
        setZoom = self.zoomSelect.currentText()
        self.setupOAV()
        th = OAVThread()
        th.ImageUpdate.connect(self.setImage)
        th.start()
        self.oav_stream.mousePressEvent = self.onMouse
        self.start.clicked.connect(self.oavStart)
        self.stop.clicked.connect(self.oavStop)
        # RBV updating connections thread
        th2 = RBVThread()
        th2.rbvUpdate.connect(self.updateRBVs)
        th2.start()
        # bls_thread = BLSThread()
        # bls_thread.safe.connect(self.updateBLS)
        # bls_thread.start()
        # gonio rotation buttons
        self.minus180.clicked.connect(lambda: self.gonioRotate(-180))
        self.plus180.clicked.connect(lambda: self.gonioRotate(180))
        self.minus90.clicked.connect(lambda: self.gonioRotate(-90))
        self.plus90.clicked.connect(lambda: self.gonioRotate(90))
        self.minus15.clicked.connect(lambda: self.gonioRotate(-15))
        self.plus15.clicked.connect(lambda: self.gonioRotate(15))
        self.minus5.clicked.connect(lambda: self.gonioRotate(-5))
        self.plus5.clicked.connect(lambda: self.gonioRotate(5))
        self.zero.clicked.connect(lambda: self.gonioRotate(0))
        # jog buttons
        self.up.clicked.connect(lambda: self.jogSample("up"))
        self.down.clicked.connect(lambda: self.jogSample("down"))
        self.left.clicked.connect(lambda: self.jogSample("left"))
        self.right.clicked.connect(lambda: self.jogSample("right"))
        # exposure and gain sliders
        self.zoomSelect.currentIndexChanged.connect(self.setZoom)
        self.sliderExposure.valueChanged.connect(self.changeExposureGain)
        self.sliderGain.valueChanged.connect(self.changeExposureGain)
        self.zeroAll.clicked.connect(self.returntozero)
        # robot buttons
        self.load.clicked.connect(self.loadNextPin)
        # testing camera start stop
        # self.up.clicked.connect(self.showRoboCam)
        # self.down.clicked.connect(self.stopRoboCam)
        # thread for setting beamline safe
        # bls_thread = BLSThread()
        # bls_thread.safe.connect(self.updateBLS)
        # bls_thread.start()

    # def updateBLS(self, safe):
    #     print(safe)
        # print(self.safe)
        # if self.safe == 1:
        #     ca.caput(ca.caput(pv.robot_ip16_force_option, "On"))
        # else:
        #     ca.caput(ca.caput(pv.robot_ip16_force_option, "No"))

    def loadNextPin(self):
        ca.caput(pv.robot_reset, 1)
        ca.caput(pv.robot_next_pin, self.spinToLoad.value())
        ca.caput(pv.robot_proc_load, 1)

    def unloadPin(self):
        ca.caput(pv.robot_reset, 1)
        ca.caput(pv.robot_proc_unload, 1)

    def dryGripper(self):
        ca.caput(pv.robot_reset, 1)
        ca.caput(pv.robot_proc_dry, 1)

    # def showRoboCam(self):
    #     th3 = Worker3()
    #     th3.run()

    # def stopRoboCam(self):
    #     th3 = Worker3()
    #     th3.stop()

    def quit(self):
        sys.exit()

    def returntozero(self):
        for motor in [pv.gonio_y, pv.gonio_z, pv.stage_z, pv.omega]:
            ca.caput(motor, 0)

    # not currently working
    def setZoom(self, level):
        setZoom = self.zoomSelect.currentText()
        th.updateZoom(int(setZoom))

    def changeExposureGain(self):
        ca.caput(pv.oav_cam_acqtime, (self.sliderExposure.value() / 100))
        ca.caput(pv.oav_cam_gain, self.sliderGain.value())

    def jogSample(self, direction):
        if direction == "left":
            ca.caput(pv.stage_z, (float(ca.caget(pv.stage_z_rbv)) + 0.005))
        elif direction == "right":
            ca.caput(pv.stage_z, (float(ca.caget(pv.stage_z_rbv)) - 0.005))
        elif direction == "up":
            ca.caput(
                pv.gonio_y,
                (float(ca.caget(pv.gonio_y_rbv)))
                + ((math.sin(math.radians(float(ca.caget(pv.omega_rbv)))))) * 0.005,
            )
            ca.caput(
                pv.gonio_z,
                (float(ca.caget(pv.gonio_z_rbv)))
                + ((math.cos(math.radians(float(ca.caget(pv.omega_rbv)))))) * 0.005,
            )
        elif direction == "down":
            ca.caput(
                pv.gonio_y,
                (float(ca.caget(pv.gonio_y_rbv)))
                - ((math.sin(math.radians(float(ca.caget(pv.omega_rbv)))))) * 0.005,
            )
            ca.caput(
                pv.gonio_z,
                (float(ca.caget(pv.gonio_z_rbv)))
                - ((math.cos(math.radians(float(ca.caget(pv.omega_rbv)))))) * 0.005,
            )
        else:
            pass

    # moving sample to beam centre when clicked
    def onMouse(self, event):
        x = event.pos().x()
        x = x * 2
        y = event.pos().y()
        y = y * 2
        x_curr = float(ca.caget(pv.stage_z_rbv))
        print(x_curr)
        y_curr = float(ca.caget(pv.gonio_y_rbv))
        z_curr = float(ca.caget(pv.gonio_z_rbv))
        omega = float(ca.caget(pv.omega_rbv))
        print("Clicked", x, y)
        Xmove = x_curr + ((x - beamX) * calibrate)
        print((x - beamX))
        Ymove = y_curr + (math.sin(math.radians(omega)) * ((y - beamY) * calibrate))
        Zmove = z_curr + (math.cos(math.radians(omega)) * ((y - beamY) * calibrate))
        print("Moving", Xmove, Ymove, Zmove)
        ca.caput(pv.stage_z, Xmove)
        ca.caput(pv.gonio_y, Ymove)
        ca.caput(pv.gonio_z, Zmove)

    def setupOAV(self):
        for callback in (
            pv.oav_roi_ecb,
            pv.oav_arr_ecb,
            pv.oav_stat_ecb,
            pv.oav_proc_ecb,
            pv.oav_over_ecb,
            pv.oav_fimg_ecb,
            pv.oav_tiff_ecb,
            pv.oav_hdf5_ecb,
            pv.oav_pva_ecb,
        ):
            ca.caput(callback, "Disable")
        ca.caput(pv.oav_mjpg_maxw, 2064)
        ca.caput(pv.oav_mjpg_maxh, 1544)

    def oavStart(self):
        ca.caput(pv.oav_acquire, "Acquire")

    def oavStop(self):
        ca.caput(pv.oav_acquire, "Done")

    def setImage(self, image):
        self.oav_stream.setPixmap(QPixmap.fromImage(image))

    def gonioRotate(self, amount):
        gonio_current = float(ca.caget(pv.omega_rbv))
        if amount == 0:
            gonio_request = 0
        else:
            gonio_request = gonio_current + amount
        print("Moving gonio omega to", str(gonio_request))
        ca.caput(pv.omega, gonio_request)

    def updateRBVs(self, rbvs):
        # stagez, gony, gonz, omega, oavexp, oavgain, currentsamp, goniosens, stagex, stagey
        self.stagez_rbv.setText(str(round(float(rbvs[0]), 3))) # used to be x now is z
        self.gony_rbv.setText(str(round(float(rbvs[1]), 3)))
        self.gonz_rbv.setText(str(round(float(rbvs[2]), 3)))
        self.omega_rbv.setText(str(round(float(rbvs[3]), 0)))
        self.exposure_rbv.setText(str(round(float(rbvs[4]), 3)))
        self.gain_rbv.setText(str(int(rbvs[5])))
        self.currentSamp.setText(str(rbvs[6]))
        blsafe = all(round(float(rbvs[x]), 3) == 0.00 for x in [0, 1, 2, 3, 8, 9])
        if blsafe:
            ca.caput(pv.robot_ip16_force_option, "On")
        else:
            ca.caput(pv.robot_ip16_force_option, "No")
        if ca.caget(pv.robot_pin_mounted) == "Yes":
            self.gonioSens.setStyleSheet("background-color: green")
        else:
            self.gonioSens.setStyleSheet("background-color: white")



if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
