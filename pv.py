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

# Gonio Omega
omega = "LA18L-MO-LSR-01:OMEGA"
omega_rbv = "LA18L-MO-LSR-01:OMEGA.RBV"
omega_tws = "LA18L-MO-LSR-01:OMEGA.TWV"
omega_tw_f = "LA18L-MO-LSR-01:OMEGA.TWF"
omega_tw_r = "LA18L-MO-LSR-01:OMEGA.TWR"

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

# robot
robot_next_pin = "LA18L-MO-ROBOT-01:NEXT_PIN"
robot_next_pin_rbv = "LA18L-MO-ROBOT-01:NEXT_PIN_RBV"
robot_current_pin_rbv = "LA18L-MO-ROBOT-01:CURRENT_PIN_RBV"
robot_pin_mounted = "LA18L-MO-ROBOT-01:PIN_MOUNTED"
robot_reset = "LA18L-MO-ROBOT-01:RESET.PROC"
robot_prog_running = "LA18L-MO-ROBOT-01:PROGRAM_RUNNING"
