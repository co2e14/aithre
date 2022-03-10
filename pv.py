#!/usr/bin/python
import os
import sys
import time


def pv_name(name):
    for pv in globals():
        if name[:2].lower() in pv.lower():
            print("PV:", pv[:])


def pv_return():
    return globals()


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