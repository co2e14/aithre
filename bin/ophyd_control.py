from bluesky import RunEngine
from ophyd import EpicsMotor
from ophyd import Device, EpicsSignal, EpicsSignalRO
from ophyd import Component as Cpt
from ophyd.utils import set_and_wait
from ophyd.sim import det
from bluesky.plans import scan
from bluesky.callbacks.best_effort import BestEffortCallback
bec = BestEffortCallback()

RE = RunEngine({})
RE.subscribe(bec)

dets = [det]
stage_x = EpicsMotor("LA18L-MO-LSR-01:X", name="stage_x")
stage_y = EpicsMotor("LA18L-MO-LSR-01:Y", name="stage_y")
stage_z = EpicsMotor("LA18L-MO-LSR-01:Z", name="stage_z")
gonio_omega = EpicsMotor("LA18L-MO-LSR-01:OMEGA", name="gonio_omega")
gonio_y = EpicsMotor("LA18L-MO-LSR-01:SAMPY", name="gonio_y")
gonio_z = EpicsMotor("LA18L-MO-LSR-01:SAMPZ", name="gonio_z")

for motor in [stage_x, stage_y, stage_z, gonio_omega, gonio_y, gonio_z]:
    motor.wait_for_connection()

# set limits
setlims = False
if setlims == True:
    stage_x.high_limit_travel.put(5)
    stage_x.low_limit_travel.put(-5)
    stage_y.high_limit_travel.put(1)
    stage_y.low_limit_travel.put(-1)
    stage_z.high_limit_travel.put(1)
    stage_z.low_limit_travel.put(-1)
    gonio_y.high_limit_travel.put(2.5)
    gonio_y.low_limit_travel.put(-2.5)
    gonio_z.high_limit_travel.put(2.5)
    gonio_z.low_limit_travel.put(-2.5)
else:
    pass



# stage_x.high_limit_travel.put(5) # sets high user limit to 5
# stage_x.user_setpoint.put(0) # move value of x to zero
# gonio_omega.velocity.set(10) # set gonio velocity to 1o deg/s





#RE(scan(dets, motor, 0.2, 0.3, motor2, 0, 1, 100))

# def get_axis():
#     for axis_pv in list(pv.axis.items()):
#         axis = str(axis_pv[0])
#         axis = EpicsMotor(axis_pv[1], name=axis_pv[0])
#         axis.wait_for_connection()
#         print(f"{axis_pv[0]} is currently at {axis.position}")

# def scan_axis(motor, low, high):
#     axis = EpicsMotor(motor)
