from bluesky import RunEngine
from ophyd import EpicsMotor
from ophyd.sim import det
import pv
import bluesky.plan_stubs as bps
from bluesky.plans import scan
from bluesky.utils import ProgressBarManager

RE = RunEngine({})
RE.waiting_hook = ProgressBarManager()

axis_pv = list(pv.axis.items())[0]

epics = EpicsMotor(axis_pv[1],name=axis_pv[0])
try:
    epics.summary()
except:
    print("ffs")
#RE(bps.mvr(epics, 0.05))

#epics.position()

print("done")

# for stage, prog_var in pv.axis.items():
#     stage = EpicsMotor(prog_var, name=stage)
#     stage.summary()
