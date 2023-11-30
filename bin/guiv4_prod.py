#!/dls/science/groups/i23/pyenvs/aithreconda/bin/python

# C Orr 2022
from PyQt5 import QtCore, QtGui, QtWidgets
import cv2 as cv
from control import ca
import pv
import math
import sys
import numpy as np
import time
import os
from guiv4 import Ui_MainWindow

# Set beam position and scale.
version = "4.2.3"

line_width = 1
line_spacing = 60
line_color = (164, 164, 164)
beamX = 1190
beamY = 736
# div 2 if using Qt gui as its half size


# pixel size 3.45, 2 to 1 imaging system so calib 1/2
calibrate = 0.00172
# calibrate = 0.00345

# separate thread for OAV
class OAVThread(QtCore.QThread):
    ImageUpdate = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self):
        super(OAVThread, self).__init__()
        self.ThreadActive = False
        self.zoomLevel = 1
        self.beamX = beamX
        self.beamY = beamY
        self.line_width = line_width
        self.line_spacing = line_spacing
        self.line_color = line_color
        
    def run(self):
        self.ThreadActive = True
        self.cap = cv.VideoCapture("http://bl23i-ea-serv-01.diamond.ac.uk:8080/OAV.mjpg.mjpg")
        while self.ThreadActive:
            ret, frame = self.cap.read()
            if self.ThreadActive and ret:
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
                
                if self.zoomLevel != 1:
                    new_width = int(frame.shape[1] / self.zoomLevel)
                    new_height = int(frame.shape[0] / self.zoomLevel)
                    
                    x1 = max(self.beamX - new_width // 2, 0)
                    y1 = max(self.beamY - new_height // 2, 0)
                    x2 = min(self.beamX + new_width // 2, frame.shape[1])
                    y2 = min(self.beamY + new_height // 2, frame.shape[0])
                    
                    x1, x2 = self.adjust_roi_boundaries(x1, x2, frame.shape[1], new_width)
                    y1, y2 = self.adjust_roi_boundaries(y1, y2, frame.shape[0], new_height)

                    cropped_frame = frame[y1:y2, x1:x2]
                    
                    frame = cv.resize(cropped_frame, (frame.shape[1], frame.shape[0]))
                    
                    

                # cv.ellipse(frame, (beamX, beamY), (12, 8), 0.0, 0.0, 360, (0,0,255), thickness=2) # could use to draw cut...
                # cv.putText(frame,'text',bottomLeftCornerOfText, font, fontScale, fontColor, thickness, lineType)
                rgbImage = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                convertToQtFormat = QtGui.QImage(
                    rgbImage.data,
                    rgbImage.shape[1],
                    rgbImage.shape[0],
                    QtGui.QImage.Format_RGB888,
                )
                p = convertToQtFormat
                p = convertToQtFormat.scaled(1032, 772, QtCore.Qt.KeepAspectRatio)
                self.ImageUpdate.emit(p)
    
    def adjust_roi_boundaries(self, start, end, max_value, window_size):
        if start < 0:
            end -= start
            start = 0
        if end > max_value:
            start -= (end - max_value)
            end = max_value
        if (end - start) < window_size and (start + window_size) <= max_value:
            end = start + window_size
        return start, end
    
    def setZoomLevel(self, zoomLevel):
        self.zoomLevel = zoomLevel

    def stop(self):
        self.ThreadActive = False
        self.cap.release()
        self.quit()

# class BLSThread(QtCore.QThread):
#     safe = QtCore.pyqtSignal(bool)

#     def run(self):
#         self.ThreadActive = True
#         while self.ThreadActive:
#             time.sleep(5)
#             for rbv in [pv.omega_rbv, pv.gonio_y_rbv, pv.gonio_z_rbv, pv.stage_x_rbv, pv.stage_y_rbv]:
#                 if round(float(ca.caget(rbv)), 1) == 0.0:
#                     safe = True
#             self.safe.emit(safe)

# separate thread to run caget for RBVs
class RBVThread(QtCore.QThread):
    rbvUpdate = QtCore.pyqtSignal(list)

    def run(self):
        self.ThreadActive = True
        while self.ThreadActive:
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


class robotCheckThread(QtCore.QThread):
    robotUpdate = QtCore.pyqtSignal(list)

    def run(self):
        self.ThreadActive = True
        while self.ThreadActive:
            robotUpdateList = []
            robotUpdateList += [str(ca.caget(pv.robot_prog_running))]
            self.robotUpdate.emit(robotUpdateList)



# not working yet. Kind of. Ish. Need to have it emit to gui
# class Worker3(QtCore.QThread):
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

class MainWindow(QtWidgets.QMainWindow):
    zoomChanged = QtCore.pyqtSignal(int)

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)        
        # setup
        self.checkIOCStatus()
        # menus
        self.ui.actionExit.triggered.connect(self.quit)
        # sliders and sensors
        self.ui.sliderExposure.setProperty(
            "value", str(round(float(ca.caget(pv.oav_cam_acqtime_rbv)) * 100))
        )
        self.ui.sliderGain.setProperty(
            "value", str(round(float(ca.caget(pv.oav_cam_gain_rbv))))
        )
        #OAV zoom setup
        self.ui.sliderZoom.valueChanged.connect(self.handleZoom)
        # OAV connections thread
        self.zoomLevel = 1
        self.setupOAV()
        self.th = OAVThread()
        self.th.ImageUpdate.connect(self.setImage)
        self.th.start()
        self.zoomChanged.connect(self.th.setZoomLevel)
        self.ui.oav_stream.mousePressEvent = self.onMouse
        self.ui.start.clicked.connect(self.oavStart)
        self.ui.stop.clicked.connect(self.oavStop)
        self.ui.snapshot.clicked.connect(self.saveSnapshot)
        # RBV updating connections thread
        th2 = RBVThread()
        th2.rbvUpdate.connect(self.updateRBVs)
        th2.start()
        # robot active thread
        th3 = robotCheckThread()
        th3.robotUpdate.connect(self.setRobotActiveStatus)
        th3.start()
        # gonio rotation buttons
        self.ui.buttonSlowOmegaTurn.clicked.connect(lambda: ca.caput(pv.omega_velo, 15))
        self.ui.buttonFastOmegaTurn.clicked.connect(lambda: ca.caput(pv.omega_velo, 150))
        self.ui.plusMinus3600.clicked.connect(self.goTopm3600)
        self.ui.minus180.clicked.connect(lambda: self.gonioRotate(-180))
        self.ui.plus180.clicked.connect(lambda: self.gonioRotate(180))
        self.ui.minus90.clicked.connect(lambda: self.gonioRotate(-90))
        self.ui.plus90.clicked.connect(lambda: self.gonioRotate(90))
        self.ui.minus15.clicked.connect(lambda: self.gonioRotate(-15))
        self.ui.plus15.clicked.connect(lambda: self.gonioRotate(15))
        self.ui.minus5.clicked.connect(lambda: self.gonioRotate(-5))
        self.ui.plus5.clicked.connect(lambda: self.gonioRotate(5))
        self.ui.zero.clicked.connect(lambda: self.gonioRotate(0))
        # jog buttons
        self.ui.up.clicked.connect(lambda: self.jogSample("up"))
        self.ui.down.clicked.connect(lambda: self.jogSample("down"))
        self.ui.left.clicked.connect(lambda: self.jogSample("left"))
        self.ui.right.clicked.connect(lambda: self.jogSample("right"))
        self.ui.pushButtonSampleIn.clicked.connect(lambda: self.jogSample("in"))
        self.ui.pushButtonSampleOut.clicked.connect(lambda: self.jogSample("out"))
        # exposure and gain sliders
        self.ui.sliderExposure.valueChanged.connect(self.changeExposureGain)
        self.ui.sliderGain.valueChanged.connect(self.changeExposureGain)
        self.ui.zeroAll.clicked.connect(self.returntozero)
        # robot buttons
        self.ui.resetRobot.clicked.connect(lambda: ca.caput(pv.robot_reset, 1))
        self.ui.load.clicked.connect(self.loadNextPin)
        self.ui.unload.clicked.connect(self.unloadPin)
        self.ui.dry.clicked.connect(self.dryGripper)
        self.ui.pushButtonIOCCheck.clicked.connect(self.checkIOCStatus)

    def loadNextPin(self):
        ca.caput(pv.robot_reset, 1)
        time.sleep(1)
        ca.caput(pv.robot_next_pin, self.ui.spinToLoad.value())
        ca.caput(pv.robot_proc_load, 1)

    def unloadPin(self):
        ca.caput(pv.robot_reset, 1)
        time.sleep(1)
        ca.caput(pv.robot_proc_unload, 1)

    def dryGripper(self):
        ca.caput(pv.robot_reset, 1)
        time.sleep(1)
        ca.caput(pv.robot_proc_dry, 1)

    def quit(self):
        sys.exit()

    def returntozero(self):
        for motor in [pv.gonio_y, pv.gonio_z, pv.stage_z, pv.omega]:
            ca.caput(motor, 0)

    def handleZoom(self, zoomValue):
        self.zoomLevel = zoomValue
        self.ui.currentZoom.setText(str(self.zoomLevel))
        self.zoomChanged.emit(self.zoomLevel)

    def changeExposureGain(self):
        ca.caput(pv.oav_cam_acqtime, (self.ui.sliderExposure.value() / 100))
        ca.caput(pv.oav_cam_gain, self.ui.sliderGain.value())

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
        elif direction == "in":
            ca.caput(
                pv.gonio_y,
                (float(ca.caget(pv.gonio_y_rbv)))
                - ((math.cos(math.radians(float(ca.caget(pv.omega_rbv)))))) * 0.05,
            )
            ca.caput(
                pv.gonio_z,
                (float(ca.caget(pv.gonio_z_rbv)))
                - ((math.sin(math.radians(float(ca.caget(pv.omega_rbv)))))) * 0.05,
            )
        elif direction == "out":
            ca.caput(
                pv.gonio_y,
                (float(ca.caget(pv.gonio_y_rbv)))
                + ((math.cos(math.radians(float(ca.caget(pv.omega_rbv)))))) * 0.05,
            )
            ca.caput(
                pv.gonio_z,
                (float(ca.caget(pv.gonio_z_rbv)))
                + ((math.sin(math.radians(float(ca.caget(pv.omega_rbv)))))) * 0.05,
            )
        else:
            pass

    def goTopm3600(self):
        gonio_current = float(ca.caget(pv.omega_rbv))
        if gonio_current <= 0:
            gonio_request = 3600
        else:
            gonio_request = -3600
        print("Moving gonio omega to", str(gonio_request))
        ca.caput(pv.omega, gonio_request)

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
        self.image = image
        zoom_level = self.ui.sliderZoom.value()
        
        self.ui.oav_stream.setPixmap(QtGui.QPixmap.fromImage(image))
        
    def saveSnapshot(self):
        image = self.image
        print(f"Q image format: {image.format()}")
        print(f"Q image bytes: {image.byteCount()}")
        print(f"Q image bytes per line: {image.bytesPerLine()}")
        width = image.width()
        height = image.height()
        bytesPerLine = image.bytesPerLine()
        data = image.bits().asstring(height * bytesPerLine)
        arr = np.frombuffer(data, dtype=np.uint8).reshape((height, width, 3))
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self.ui.centralwidget,"QFileDialog.getSaveFileName()","","JPEG Files (*.jpg);;All Files (*)", options=options)
        
        if file_name:
            _, file_extension = os.path.splitext(file_name)
            if not file_extension:
                file_name += ".jpg"
            try:
                result = cv.imwrite(file_name, arr)
                if result:
                    print("Image saved successfully.")
                else:
                    print("Failed to save image. Try as a .jpg")
            except Exception as e:
                print(f"An error occurred while saving the image: {e}")

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
        self.ui.stagez_rbv.setText(str(round(float(rbvs[0]), 3))) # used to be x now is z
        self.ui.gony_rbv.setText(str(round(float(rbvs[1]), 3)))
        self.ui.gonz_rbv.setText(str(round(float(rbvs[2]), 3)))
        # stop -0.0 to 0.0 jitter on GUI
        if round(float(rbvs[3]), 0) == -0.0:
            self.ui.omega_rbv.setText("0.0")
        else:
            self.ui.omega_rbv.setText(str(round(float(rbvs[3]), 0)))
        self.ui.exposure_rbv.setText(str(round(float(rbvs[4]), 3)))
        self.ui.gain_rbv.setText(str(int(rbvs[5])))
        self.ui.currentSamp.setText(str(rbvs[6]))
        blsafe = all(round(float(rbvs[x]), 3) == 0.00 for x in [0, 1, 2, 3, 8, 9])
        if blsafe:
            ca.caput(pv.robot_ip16_force_option, "On")
            self.ui.indicatorBeamlineSafe.setStyleSheet("background-color: green")
        else:
            ca.caput(pv.robot_ip16_force_option, "No")
            self.ui.indicatorBeamlineSafe.setStyleSheet("background-color: red")
        if ca.caget(pv.robot_pin_mounted) == "Yes":
            self.ui.indicatorGonioSensor.setStyleSheet("background-color: green")
        else:
            self.ui.indicatorGonioSensor.setStyleSheet("background-color: red")

    def setRobotActiveStatus(self, robotUpdateList):
        if str(robotUpdateList[0]) == "No":
            self.ui.indicatorRobotActive.setStyleSheet("background-color: red")
        else:
            self.ui.indicatorRobotActive.setStyleSheet("background-color: green")

    def checkIOCStatus(self):
        try:
            ca.caget(pv.omega_rbv)
            self.ui.indicatorMotionIOC.setStyleSheet("background-color: green")
        except:
            self.ui.indicatorMotionIOC.setStyleSheet("background-color: red")
        try:
            ca.caget(pv.oav_cam_gain_rbv)
            self.ui.indicatorOAVIOC.setStyleSheet("background-color: green")
        except:
            self.ui.indicatorOAVIOC.setStyleSheet("background-color: red")
        try:
            ca.caget(pv.robot_next_pin_rbv)
            self.ui.indicatorRobotIOC.setStyleSheet("background-color: green")
        except:
            self.ui.indicatorRobotIOC.setStyleSheet("background-color: red")
        self.ui.indicatorZoomIOC.setStyleSheet("background-color: red")
        # try:
        #     ca.caget(pv.zoom_dud)
        # except:
        #     print("no zoom?")
        # need to figure out a way for this to not loop trying to find the dud PV.


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
