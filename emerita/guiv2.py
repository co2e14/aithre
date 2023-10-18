#!/usr/bin/env /dls_sw/i23/scripts/ctrl_conda/bin/python
import sys

if sys.version_info[0] >= 3:
    import PySimpleGUIQt as sg
else:
    import PySimpleGUI27 as sg
import cv2
import numba as np
from numpy import full as full
from sys import exit as exit
import time
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pv
import bin.control as control
import cothread
from cothread.catools import caput, caget, cainfo

def main():

    sg.ChangeLookAndFeel("")

    # define the window layout
    layout = [
        [sg.Text("Aithre", size=(60, 1), justification="left", font="Any 28")],
        [sg.Image(filename="", key="image")],
        [sg.Text("Camera Control")],
        [
            sg.Button("Start", size=(10, 1), font="Any 14"),
            sg.Button("Stop", size=(10, 1), font="Any 14"),
        ],
        [sg.Text("X/Z Stage"),],
        [
            sg.Text("X Current"),
            sg.Text(key="stage_x_rbv"),
            sg.Text("X Set"),
            sg.InputText("", size=(10, 1), font="Consolas 10", key="Xstage_set"),
        ],
        [
            sg.Text("Z Current"),
            sg.Text(key="stage_z_rbv"),
            sg.Text("Z Set"),
            sg.InputText("", size=(10, 1), font="Consolas 10", key="Zstage_set"),
        ],
        [
            sg.Text("Laser Y"),
            sg.Text(key="stage_y_rbv"),
            sg.Text("Laser Y Set"),
            sg.InputText("", size=(10, 1), font="Consolas 10", key="Ystage_set"),
        ],
        [
            sg.Text("Jog (um)"),
            sg.InputText("0.1", size=(7, 1), font="Consolas 10", key="XZstage_joginc"),
            sg.Button("<- X", size=(5, 1), font="Any 10", key="X-"),
            sg.Button("X ->", size=(5, 1), font="Any 10", key="X+"),
            sg.Button("Z -", size=(5, 1), font="Any 10", key="Z-"),
            sg.Button("Z +", size=(5, 1), font="Any 10", key="Z+"),
        ],
        [sg.Button("Exit", size=(10, 1), font="Any 14"),],
    ]

    rbvs = ["stage_x_rbv", "stage_z_rbv", "stage_y_rbv"]
    stage_tws = ["stage_x_tws", "stage_z_tws", "stage_y_tws"]

    # create the window and show it without the plot
    window = sg.Window("I23 Laser Shaping System - Aithre", location=(800, 400))
    window.Layout(layout)

    # ---===--- Event LOOP Read and display frames, operate the GUI --- #
    cap = cv2.VideoCapture('http://ws464.diamond.ac.uk:8080/OAV.mjpg.mjpg')
    recording = False
    while True:
        event, values = window.Read(timeout=0, timeout_key="timeout")
        if event == "Exit" or event is None:
            sys.exit(0)
            pass
        elif event == "Start":
            recording = True
        elif event == "Stop":
            recording = False
            img = full((480, 640), 255)
            imgbytes = cv2.imencode(".png", img)[
                1
            ].tobytes()  # this is faster, shorter and needs less includes
            window.FindElement("image").Update(data=imgbytes)
        if event == "<- X" or "X ->" or "Z -" or "Z +":
            for tw in stage_tws:
                caput(getattr(pv, tw), float(values["XZstage_joginc"]))
        if event == "X-":
            caput(pv.stage_x_tw_f, 1)
        if event == "X+":
            caput(pv.stage_x_tw_r, 1)
        if event == "Z-":
            caput(pv.stage_z_tw_f, 1)
        if event == "Z+":
            caput(pv.stage_z_tw_r, 1)
        if recording:
            ret, frame = cap.read()
            imgbytes = cv2.imencode(".png", frame)[1].tobytes()  # ditto
            window.FindElement("image").Update(data=imgbytes)
        # update rbvs
        for rbv in rbvs:
            window.FindElement("{}".format(rbv)).Update(
                caget(getattr(pv, rbv))
            )
        


main()
exit()

if __name__ == '__main__':
    main()