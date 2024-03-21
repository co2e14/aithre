#!/usr/bin/python
import os
import sys
import time


# XZ stages
stage_x = "LA18L-MO-LSR-01:X"
stage_x_rbv = "LA18L-MO-LSR-01:X.RBV"
stage_x_tws = "LA18L-MO-LSR-01:X.TWV"
stage_x_tw_f = "LA18L-MO-LSR-01:X.TWF"
stage_x_tw_r = "LA18L-MO-LSR-01:X.TWR"
stage_x_movn = "LA18L-MO-LSR-01:X.MOVN"
stage_z = "LA18L-MO-LSR-01:Z"
stage_z_rbv = "LA18L-MO-LSR-01:Z.RBV"
stage_z_tws = "LA18L-MO-LSR-01:Z.TWV"
stage_z_tw_f = "LA18L-MO-LSR-01:Z.TWF"
stage_z_tw_r = "LA18L-MO-LSR-01:Z.TWR"

# Y
stage_y = "LA18L-MO-LSR-01:Y"
stage_y_rbv = "LA18L-MO-LSR-01:Y.RBV"
stage_y_tws = "LA18L-MO-LSR-01:Y.TWV"
stage_y_tw_f = "LA18L-MO-LSR-01:Y.TWF"
stage_y_tw_r = "LA18L-MO-LSR-01:Y.TWR"

# Gonio YZ
gonio_z = "LA18L-MO-LSR-01:SAMPZ"
gonio_z_rbv = "LA18L-MO-LSR-01:SAMPZ.RBV"
gonio_z_tws = "LA18L-MO-LSR-01:SAMPZ.TWV"
gonio_z_tw_f = "LA18L-MO-LSR-01:SAMPZ.TWF"
gonio_z_tw_r = "LA18L-MO-LSR-01:SAMPZ.TWR"
gonio_y = "LA18L-MO-LSR-01:SAMPY"
gonio_y_rbv = "LA18L-MO-LSR-01:SAMPY.RBV"
gonio_y_tws = "LA18L-MO-LSR-01:SAMPY.TWV"
gonio_y_tw_f = "LA18L-MO-LSR-01:SAMPY.TWF"
gonio_y_tw_r = "LA18L-MO-LSR-01:SAMPY.TWR"
gonio_y_movn = "LA18L-MO-LSR-01:SAMPY.MOVN"
gonio_z_movn = "LA18L-MO-LSR-01:SAMPZ.MOVN"

# Gonio Omega
omega = "LA18L-MO-LSR-01:OMEGA"
omega_rbv = "LA18L-MO-LSR-01:OMEGA.RBV"
omega_tws = "LA18L-MO-LSR-01:OMEGA.TWV"
omega_tw_f = "LA18L-MO-LSR-01:OMEGA.TWF"
omega_tw_r = "LA18L-MO-LSR-01:OMEGA.TWR"
omega_velo = "LA18L-MO-LSR-01:OMEGA.VELO"

# OAV
oav_acquire = "LA18L-DI-OAV-01:CAM:Acquire"
oav_mjpg_maxw = "LA18L-DI-OAV-01:MJPG:MAXW"
oav_mjpg_maxh = "LA18L-DI-OAV-01:MJPG:MAXH"
oav_cam_acqtime = "LA18L-DI-OAV-01:CAM:AcquireTime"
oav_cam_acqtime_rbv = "LA18L-DI-OAV-01:CAM:AcquireTime_RBV"
oav_cam_gain = "LA18L-DI-OAV-01:CAM:Gain"
oav_cam_gain_rbv = "LA18L-DI-OAV-01:CAM:Gain_RBV"
oav_roi_ecb = "LA18L-DI-OAV-01:ROI:EnableCallbacks"
oav_stat_ecb = "LA18L-DI-OAV-01:STAT:EnableCallbacks"
oav_arr_ecb = "LA18L-DI-OAV-01:ARR:EnableCallbacks"
oav_proc_ecb = "LA18L-DI-OAV-01:PROC:EnableCallbacks"
oav_over_ecb = "LA18L-DI-OAV-01:OVER:EnableCallbacks"
oav_fimg_ecb = "LA18L-DI-OAV-01:FIMG:EnableCallbacks"
oav_tiff_ecb = "LA18L-DI-OAV-01:TIFF:EnableCallbacks"
oav_hdf5_ecb = "LA18L-DI-OAV-01:HDF5:EnableCallbacks"
oav_pva_ecb = "LA18L-DI-OAV-01:PVA:EnableCallbacks"
oav_max_x = "LA18L-DI-OAV-01:CAM:MaxSizeX_RBV" # max sensor width
oav_max_y = "LA18L-DI-OAV-01:CAM:MaxSizeY_RBV" # max sensor height

# robot
robot_next_pin = "LA18L-MO-ROBOT-01:NEXT_PIN"
robot_next_pin_rbv = "LA18L-MO-ROBOT-01:NEXT_PIN_RBV"
robot_current_pin_rbv = "LA18L-MO-ROBOT-01:CURRENT_PIN_RBV"
robot_pin_mounted = "LA18L-MO-ROBOT-01:PIN_MOUNTED"
robot_reset = "LA18L-MO-ROBOT-01:RESET.PROC"
robot_prog_running = "LA18L-MO-ROBOT-01:PROGRAM_RUNNING"
robot_proc_soak = "LA18L-MO-ROBOT-01:SOAK.PROC"
robot_proc_dispose = "LA18L-MO-ROBOT-01:DISP.PROC"
robot_proc_unload = "LA18L-MO-ROBOT-01:UNLD.PROC"
robot_proc_gotohome = "LA18L-MO-ROBOT-01:GOHM.PROC"
robot_proc_load = "LA18L-MO-ROBOT-01:LOAD.PROC"
robot_proc_dry = "LA18L-MO-ROBOT-01:DRY.PROC"
robot_gripper_temp = "LA18L-MO-ROBOT-01:GRIPPER_TEMP"
robot_ip16_force_option = "LA18L-MO-ROBOT-01:IP_16_FORCE_OPTION"

#fake zoom pv
zoom_dud = "LA18L-DI-ZOOM-01:IDONTEXIST"