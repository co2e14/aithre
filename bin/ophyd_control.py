import pv
import bluesky
import ophyd
from bluesky import RunEngine
from ophyd import EpicsMotor
from ophyd import Device, EpicsSignal, EpicsSignalRO
from ophyd import Component as Cpt
from ophyd.utils import set_and_wait
from bluesky.callbacks.best_effort import BestEffortCallback
bec = BestEffortCallback()

RE = RunEngine({})
RE.subscribe(bec)

def getaxis():
    for axis_pv in list(pv.axis.items()):
        axis = str(axis_pv[0])
        axis = EpicsMotor(axis_pv[1], name=axis_pv[0])
        axis.wait_for_connection()
        print(f"{axis_pv[0]} is currently at {axis.position}")


