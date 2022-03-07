# C Orr 2022
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PIL import Image, ImageTk
import cv2 as cv
from control import ca
import pv
import math

# Set beam position and scale.
beamX = 1080
beamY = 748
# div 2 if using Qt gui as its half size


# pixel size 3.45, 2 to 1 imaging system so calib 1/2 
calibrate = 0.00172
#calibrate = 0.00345


class Worker1(QThread):
    ImageUpdate = pyqtSignal(QImage)

    def run(self):
        self.ThreadActive = True
        cap = cv.VideoCapture("http://ws464.diamond.ac.uk:8080/OAV.mjpg.mjpg")
        while self.ThreadActive:
            ret, frame = cap.read()
            if self.ThreadActive:
                cv.line(
                    frame, (beamX - 10, beamY), (beamX + 10, beamY), (0, 255, 0), 2,
                )
                cv.line(
                    frame, (beamX, beamY - 10), (beamX, beamY + 10), (0, 255, 0), 2,
                )
                # cv.ellipse(frame, (beamX, beamY), (12, 8), 0.0, 0.0, 360, (0,0,255), thickness=2) # could use to draw cut...
                # putText(frame,'text',bottomLeftCornerOfText, font, fontScale, fontColor, thickness, lineType)
                cv.putText(
                    frame,
                    "Key bindings",
                    (20, 40),
                    cv.FONT_HERSHEY_COMPLEX_SMALL,
                    1.0,
                    (0, 255, 255),
                    1,
                    1,
                )
                cv.putText(
                    frame,
                    "esc : close window",
                    (25, 60),
                    cv.FONT_HERSHEY_COMPLEX_SMALL,
                    0.8,
                    (0, 255, 255),
                    1,
                    1,
                )
                rgbImage = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                convertToQtFormat = QtGui.QImage(
                    rgbImage.data,
                    rgbImage.shape[1],
                    rgbImage.shape[0],
                    QtGui.QImage.Format_RGB888,
                )
                p = convertToQtFormat
                p = convertToQtFormat.scaled(1032, 772, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(p)

    def stop(self):
        self.ThreadActive = False
        self.quit()


class Ui_MainWindow(object):
    def __init__(self):
        super().__init__()

    def setImage(self, image):
        self.oav_stream.setPixmap(QPixmap.fromImage(image))

    def onMouse(self, event):
        x = event.pos().x()
        x = x * 2
        y = event.pos().y()
        y = y * 2
        x_curr = float(ca.caget(pv.stage_x_rbv))
        print(x_curr)
        y_curr = float(ca.caget(pv.gonio_y_rbv))
        z_curr = float(ca.caget(pv.gonio_z_rbv))
        omega = float(ca.caget(pv.omega_rbv))
        print("Clicked", x, y)
        Xmove = x_curr - ((x - beamX) * calibrate)
        print((x - beamX))
        Ymove = y_curr + (math.sin(math.radians(omega)) * ((y - beamY) * calibrate))
        Zmove = z_curr + (math.cos(math.radians(omega)) * ((y - beamY) * calibrate))
        print("Moving", Xmove, Ymove, Zmove)
        ca.caput(pv.stage_x, Xmove)
        ca.caput(pv.gonio_y, Ymove)
        ca.caput(pv.gonio_z, Zmove)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1020, 999)
        MainWindow.setMinimumSize(QtCore.QSize(0, 0))
        MainWindow.setMaximumSize(QtCore.QSize(10000, 10000))
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
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setObjectName("frame")
        self.robot_grid = QtWidgets.QGridLayout(self.frame)
        self.robot_grid.setObjectName("robot_grid")
        self.currentsamp = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.currentsamp.sizePolicy().hasHeightForWidth())
        self.currentsamp.setSizePolicy(sizePolicy)
        self.currentsamp.setAutoFillBackground(False)
        self.currentsamp.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.currentsamp.setObjectName("currentsamp")
        self.robot_grid.addWidget(self.currentsamp, 0, 1, 1, 1)
        self.unload = QtWidgets.QPushButton(self.frame)
        self.unload.setObjectName("unload")
        self.robot_grid.addWidget(self.unload, 3, 0, 1, 1)
        self.currentsamp_lab = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.currentsamp_lab.sizePolicy().hasHeightForWidth()
        )
        self.currentsamp_lab.setSizePolicy(sizePolicy)
        self.currentsamp_lab.setObjectName("currentsamp_lab")
        self.robot_grid.addWidget(self.currentsamp_lab, 0, 0, 1, 1)
        self.dry = QtWidgets.QPushButton(self.frame)
        self.dry.setObjectName("dry")
        self.robot_grid.addWidget(self.dry, 3, 1, 1, 1)
        self.spinBox = QtWidgets.QSpinBox(self.frame)
        self.spinBox.setProperty("showGroupSeparator", False)
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(16)
        self.spinBox.setObjectName("spinBox")
        self.robot_grid.addWidget(self.spinBox, 2, 1, 1, 1)
        self.load = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.load.sizePolicy().hasHeightForWidth())
        self.load.setSizePolicy(sizePolicy)
        self.load.setObjectName("load")
        self.robot_grid.addWidget(self.load, 2, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(
            20,
            40,
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.MinimumExpanding,
        )
        self.robot_grid.addItem(spacerItem, 1, 0, 1, 2)
        self.gridLayout.addWidget(self.frame, 2, 4, 1, 1)
        self.stop = QtWidgets.QPushButton(self.centralwidget)
        self.stop.setObjectName("stop")
        self.gridLayout.addWidget(self.stop, 1, 2, 1, 1)
        self.start = QtWidgets.QPushButton(self.centralwidget)
        self.start.setObjectName("start")
        # self.start.clicked.connect(self.oavStart)
        self.gridLayout.addWidget(self.start, 1, 0, 1, 1)
        self.frame1 = QtWidgets.QFrame(self.centralwidget)
        self.frame1.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame1.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame1.setObjectName("frame1")
        self.readback_grid = QtWidgets.QGridLayout(self.frame1)
        self.readback_grid.setObjectName("readback_grid")
        self.label = QtWidgets.QLabel(self.frame1)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.readback_grid.addWidget(self.label, 0, 0, 1, 1)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.frame1)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.readback_grid.addWidget(self.lineEdit_3, 2, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.frame1)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.readback_grid.addWidget(self.label_2, 1, 0, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(self.frame1)
        self.lineEdit.setText("")
        self.lineEdit.setObjectName("lineEdit")
        self.readback_grid.addWidget(self.lineEdit, 0, 1, 1, 1)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.frame1)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.readback_grid.addWidget(self.lineEdit_2, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.frame1)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.readback_grid.addWidget(self.label_3, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.frame1, 2, 2, 1, 1)
        self.snapshot = QtWidgets.QPushButton(self.centralwidget)
        self.snapshot.setObjectName("snapshot")
        self.gridLayout.addWidget(self.snapshot, 1, 4, 1, 1)
        self.frame2 = QtWidgets.QFrame(self.centralwidget)
        self.frame2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame2.setObjectName("frame2")
        self.motion_grid = QtWidgets.QGridLayout(self.frame2)
        self.motion_grid.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.motion_grid.setSpacing(5)
        self.motion_grid.setObjectName("motion_grid")
        self.minus180 = QtWidgets.QPushButton(self.frame2)
        self.minus180.setObjectName("minus180")
        self.motion_grid.addWidget(self.minus180, 5, 2, 1, 1)
        self.plus180 = QtWidgets.QPushButton(self.frame2)
        self.plus180.setObjectName("plus180")
        self.motion_grid.addWidget(self.plus180, 4, 2, 1, 1)
        self.plus5 = QtWidgets.QPushButton(self.frame2)
        self.plus5.setObjectName("plus5")
        self.motion_grid.addWidget(self.plus5, 3, 2, 1, 1)
        self.minus5 = QtWidgets.QPushButton(self.frame2)
        self.minus5.setObjectName("minus5")
        self.motion_grid.addWidget(self.minus5, 3, 0, 1, 1)
        self.minus15 = QtWidgets.QPushButton(self.frame2)
        self.minus15.setObjectName("minus15")
        self.motion_grid.addWidget(self.minus15, 5, 0, 1, 1)
        self.up = QtWidgets.QPushButton(self.frame2)
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
        self.down = QtWidgets.QPushButton(self.frame2)
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
        self.plus90 = QtWidgets.QPushButton(self.frame2)
        self.plus90.setObjectName("plus90")
        self.motion_grid.addWidget(self.plus90, 4, 1, 1, 1)
        self.right = QtWidgets.QPushButton(self.frame2)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.right.sizePolicy().hasHeightForWidth())
        self.right.setSizePolicy(sizePolicy)
        self.right.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("right.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.right.setIcon(icon3)
        self.right.setIconSize(QtCore.QSize(60, 60))
        self.right.setObjectName("right")
        self.motion_grid.addWidget(self.right, 1, 2, 1, 1)
        self.zero = QtWidgets.QPushButton(self.frame2)
        self.zero.setObjectName("zero")
        self.motion_grid.addWidget(self.zero, 3, 1, 1, 1)
        self.left = QtWidgets.QPushButton(self.frame2)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.left.sizePolicy().hasHeightForWidth())
        self.left.setSizePolicy(sizePolicy)
        self.left.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("left.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.left.setIcon(icon4)
        self.left.setIconSize(QtCore.QSize(60, 60))
        self.left.setObjectName("left")
        self.motion_grid.addWidget(self.left, 1, 0, 1, 1)
        self.plu15 = QtWidgets.QPushButton(self.frame2)
        self.plu15.setObjectName("plu15")
        self.motion_grid.addWidget(self.plu15, 4, 0, 1, 1)
        self.minus90 = QtWidgets.QPushButton(self.frame2)
        self.minus90.setObjectName("minus90")
        self.motion_grid.addWidget(self.minus90, 5, 1, 1, 1)
        self.gridLayout.addWidget(self.frame2, 2, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
        )
        self.gridLayout.addItem(spacerItem1, 2, 1, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
        )
        self.gridLayout.addItem(spacerItem2, 2, 3, 1, 1)
        self.oav_stream = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.oav_stream.sizePolicy().hasHeightForWidth())
        th = Worker1()
        th.ImageUpdate.connect(self.setImage)
        th.start()
        self.oav_stream.setSizePolicy(sizePolicy)
        self.oav_stream.setText("")
        self.oav_stream.setPixmap(QtGui.QPixmap(""))
        self.oav_stream.mousePressEvent = self.onMouse
        self.oav_stream.setScaledContents(True)
        self.oav_stream.setAlignment(QtCore.Qt.AlignCenter)
        self.oav_stream.setObjectName("oav_stream")
        self.gridLayout.addWidget(self.oav_stream, 0, 0, 1, 5)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1020, 20))
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
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(
            _translate("MainWindow", "Aithre v4.0 - I23 Laser Shaping")
        )
        self.currentsamp.setText(_translate("MainWindow", "None"))
        self.unload.setText(_translate("MainWindow", "Unload"))
        self.currentsamp_lab.setText(_translate("MainWindow", "Current Sample"))
        self.dry.setText(_translate("MainWindow", "Dry"))
        self.load.setText(_translate("MainWindow", "Load"))
        self.stop.setText(_translate("MainWindow", "Stop"))
        self.start.setText(_translate("MainWindow", "Start"))
        self.label.setText(_translate("MainWindow", "X"))
        self.label_2.setText(_translate("MainWindow", "Y"))
        self.label_3.setText(_translate("MainWindow", "Omega"))
        self.snapshot.setText(_translate("MainWindow", "Snapshot"))
        self.minus180.setText(_translate("MainWindow", "-180"))
        self.plus180.setText(_translate("MainWindow", "+180"))
        self.plus5.setText(_translate("MainWindow", "+5"))
        self.minus5.setText(_translate("MainWindow", "-5"))
        self.minus15.setText(_translate("MainWindow", "-15"))
        self.plus90.setText(_translate("MainWindow", "+90"))
        self.zero.setText(_translate("MainWindow", "0"))
        self.plu15.setText(_translate("MainWindow", "+15"))
        self.minus90.setText(_translate("MainWindow", "-90"))
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


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
