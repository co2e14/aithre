import numpy as np
import tkinter as tk
from tkinter import Button, Label, Tk, Entry, PhotoImage, OptionMenu
from PIL import Image, ImageTk
import cv2 as cv
import os
import datetime
import subprocess
import pv
from bin.control import ca
import os, re, sys
import math, time, string, inspect
from datetime import datetime
from time import sleep

# Set beam position and scale.
beamX = 843
beamY = 576

# 1 pixel = 2um, convert from mm to um
calibrate = 0.002

# Register clicks and move chip stages
def onMouse(event, x, y, flags, param):
    if event == cv.EVENT_LBUTTONUP:
        x_curr = float(ca.caget(pv.stage_x_rbv))
        y_curr = float(ca.caget(pv.gonio_y_rbv))
        z_curr = float(ca.caget(pv.gonio_z_rbv))
        omega = float(ca.caget(pv.omega_rbv))
        print("Clicked", x, y)
        print("Moving", xmove, ymove)
        Xmove = (x - beamX) * calibrate
        Ymove = math.cos(math.radians(omega)) * (y - beamY) * calibrate
        Zmove = math.sin(math.radians(omega)) * (y - beamY) * calibrate
        print("Moving", Xmove, Ymove, Zmove)
        

# Create a video caputure from OAV1
cap = cv.VideoCapture("http://ws464.diamond.ac.uk:8080/OAV.mjpg.mjpg")

# Create window named OAV1view and set onmouse to this
cv.namedWindow('OAVview')
cv.setMouseCallback('OAVview', onMouse)

print('Showing camera feed. Press escape to close')
# Read captured video and store them in success and frame
success, frame = cap.read()

# Loop until escape key is pressed. Keyboard shortcuts here
while success:
    success, frame = cap.read()

    cv.ellipse(frame, (beamX, beamY), (12, 8), 0.0, 0.0, 360, (0,0,255), thickness=2)
    #putText(frame,'text',bottomLeftCornerOfText, font, fontScale, fontColor, thickness, lineType)
    cv.putText(frame,'Key bindings', (20,40), cv.FONT_HERSHEY_COMPLEX_SMALL, 1, (0,255,255), 1, 1)
    cv.putText(frame,'Q / A : go to / set as f0', (25,70), cv.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0,255,255), 1, 1)
    cv.putText(frame,'W / S : go to / set as f1', (25,90), cv.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0,255,255), 1, 1)
    cv.putText(frame,'E / D : go to / set as f2', (25,110), cv.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0,255,255), 1, 1)
    cv.putText(frame,'I / O : in /out of focus', (25,130), cv.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0,255,255), 1, 1)
    cv.putText(frame,'C : Create CS', (25,150), cv.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0,255,255), 1, 1)
    cv.putText(frame,'esc : close window', (25,170), cv.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0,255,255), 1, 1)
    cv.imshow('OAVview', frame)
    
    k = cv.waitKey(1)
    if k == 0x1b: #esc
        cv.destroyWindow('OAV1view')
        print('Pressed escape. Closing window')
        break

cap.release()