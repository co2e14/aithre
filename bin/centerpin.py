import cv2 as cv
import numpy as np
from control import ca
import pv
import time
import matplotlib.pyplot as plt
import math
from bluesky import RunEngine
import bluesky.plan_stubs as bps
from ophyd import EpicsMotor, Component, Device
from bluesky.callbacks.best_effort import BestEffortCallback

bec = BestEffortCallback()
RE = RunEngine({})
RE.subscribe(bec)

beamX = 1058
beamY = 710
# div 2 if using Qt gui as its half size
# pixel size 3.45, 2 to 1 imaging system so calib 1/2
calibrate = 0.00172


class XYZStage(Device):
    stage_x = Component(EpicsMotor, "X", name="stage_x")
    stage_z = Component(EpicsMotor, "Z", name="stage_z")
    stage_y = Component(EpicsMotor, "Y", name="stage_y")
    gonio_y = Component(EpicsMotor, "SAMPY", name="gonio_y")
    gonio_z = Component(EpicsMotor, "SAMPZ", name="gonio_z")
    omega = Component(EpicsMotor, "OMEGA", name="omega")


laser_xyz_stage = XYZStage(prefix="LA18L-MO-LSR-01:", name="laser_stage")
laser_xyz_stage.wait_for_connection()

# for motor in [stage_x, stage_z, stage_y, gonio_y, gonio_z, omega]:
#     motor.wait_for_connection()


cap = cv.VideoCapture("http://ws464.diamond.ac.uk:8080/OAV.mjpg.mjpg")


def edge():
    cap = cv.VideoCapture("http://ws464.diamond.ac.uk:8080/OAV.mjpg.mjpg")
    ret, frame = cap.read()
    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # remove dead pixels in middle of camera
    deadpix = np.where(frame[:] >= 245)
    background = int(frame[735, 1150])
    frame[deadpix] = background

    blurred = cv.GaussianBlur(frame, (3, 3), 0)
    edge = cv.Canny(image=frame, threshold1=200 / 3, threshold2=200)

    # plt.figure(figsize=(10,10))
    # plt.imshow(edge)
    # plt.show()

    # find tip and middle of it QWIK MAFFS
    try:
        tip = np.max(np.nonzero(edge)[1])
        print(tip)
        width = np.nonzero([row[tip] for row in edge])[0]
        print(width)
        mid = int(np.round(sum(width) / len(width)))
    except:
        mid = 0
        tip = 0
    return mid, tip


def get_focus():
    cap = cv.VideoCapture("http://ws464.diamond.ac.uk:8080/OAV.mjpg.mjpg")
    ret, frame = cap.read()
    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    deadpix = np.where(frame[:] >= 245)
    background = int(frame[735, 1150])
    frame[deadpix] = background
    blurred = cv.GaussianBlur(frame, (3, 3), 0)
    focal_val = cv.Canny(blurred, threshold1=255 / 3, threshold2=255, L2gradient=True)
    focal_val = focal_val.sum(0).sum(0)
    return focal_val


from typing import Any, TypeVar

from ophyd import StatusBase
from ophyd.status import SubscriptionStatus

T = TypeVar("T")


def await_value(subscribable: Any, expected_value: T) -> StatusBase:
    def value_is(value, **_):
        return value == expected_value

    return SubscriptionStatus(subscribable, value_is)


def my_plan(xyz_stage):
    yield from bps.abs_set(xyz_stage.omega.user_setpoint, 0)
    await_value(xyz_stage.omega.user_readback, 0).wait(30)

    print("Finished waiting")

    best_focus_y = 0
    max_focus_val = 0
    for focus_depth in np.arange(-0.3, 0.4, 0.1):
        yield from bps.mv(xyz_stage.gonio_y, focus_depth)
        # ca.caput(pv.gonio_y, focus_depth)
        # time.sleep(0.1)
        # while int(ca.caget(pv.gonio_y_movn)) == 1:
        #     time.sleep(0.1)
        focal = get_focus()
        print(f"Focal value at {focus_depth} is {focal}")

        if int(focal) >= max_focus_val:
            max_focus_val = int(focal)
            best_focus_y = focus_depth
        else:
            pass

    print(
        f"best focus value of {max_focus_val} at {best_focus_y}. Moving to {np.round(best_focus_y, 1)}"
    )
    yield from bps.mv(xyz_stage.gonio_y, best_focus_y)
    # ca.caput(pv.gonio_y, best_focus_y)
    # time.sleep(0.1)
    # while int(ca.caget(pv.gonio_y_movn)) == 1:
    #     time.sleep(0.1)

    yield from bps.abs_set(xyz_stage.omega.user_setpoint, 90)
    await_value(xyz_stage.omega.user_readback, 90).wait(15)
    # ca.caput(pv.omega, 90)
    # while np.round(float(ca.caget(pv.omega_rbv))) != 90:
    #     time.sleep(0.1)
    best_focus_z = 0
    max_focus_val = 0
    for focus_depth in np.arange(-0.3, 0.4, 0.1):
        yield from bps.mv(xyz_stage.gonio_z, focus_depth)
        # ca.caput(pv.gonio_z, focus_depth)
        # time.sleep(0.1)
        # while int(ca.caget(pv.gonio_z_movn)) == 1:
        #     time.sleep(0.1)
        focal = get_focus()
        print(f"Focal value at {focus_depth} is {focal}")

        if int(focal) >= max_focus_val:
            max_focus_val = int(focal)
            best_focus_z = focus_depth
        else:
            pass

    print(
        f"best focus value of {max_focus_val} at {best_focus_z}. Moving to {np.round(best_focus_z, 1)}"
    )
    yield from bps.mv(xyz_stage.gonio_z, best_focus_z)
    # ca.caput(pv.gonio_z, best_focus_z)
    # time.sleep(0.1)
    # while int(ca.caget(pv.gonio_z_movn)) == 1:
    #     time.sleep(0.1)

    for omega_val in range(0, 190, 10):

        yield from bps.mv(xyz_stage.omega.user_setpoint, omega_val)
        await_value(xyz_stage.omega.user_readback, omega_val).wait(10)
        # ca.caput(pv.omega, omega_val)
        # while np.round(float(ca.caget(pv.omega_rbv))) != omega_val:
        #     time.sleep(0.1)
        goto_y, goto_x = edge()
        print(f"Going to XY coor {goto_x}, {goto_y} for omega value {omega_val}")

        if int(goto_y) == 0:
            pass
        else:
            x_curr = xyz_stage.stage_x.position
            y_curr = xyz_stage.gonio_y.position
            z_curr = xyz_stage.gonio_z.position
            omega = xyz_stage.omega.position

            # x_curr = float(ca.caget(pv.stage_x_rbv))
            # y_curr = float(ca.caget(pv.gonio_y_rbv))
            # z_curr = float(ca.caget(pv.gonio_z_rbv))
            # omega = float(ca.caget(pv.omega_rbv))
            Xmove = x_curr - ((goto_x - beamX) * calibrate)
            Ymove = y_curr + (
                math.sin(math.radians(omega)) * ((goto_y - beamY) * calibrate)
            )
            Zmove = z_curr + (
                math.cos(math.radians(omega)) * ((goto_y - beamY) * calibrate)
            )
            yield from bps.mv(xyz_stage.stage_x, Xmove, xyz_stage.gonio_y, Ymove, xyz_stage.gonio_z, Zmove)
            # ca.caput(pv.stage_x, Xmove)
            # ca.caput(pv.gonio_y, Ymove)
            # ca.caput(pv.gonio_z, Zmove)
            # while (
            #     (int(ca.caget(pv.gonio_z_movn)) == 1)
            #     or (int(ca.caget(pv.gonio_y_movn)) == 1)
            #     or (int(ca.caget(pv.stage_x_movn)) == 1)
            # ):
            #     time.sleep(0.1)


RE(my_plan(laser_xyz_stage))


raise Exception()

ca.caput(pv.omega, 0)
while np.round(float(ca.caget(pv.omega_rbv))) != 0:
    time.sleep(0.1)
