from psychopy import visual, core
import numpy as np
import pandas as pd
import src.lib as lib
# import pickle
from datetime import datetime
import copy
import os
import nidaqmx


# Variables set up
cursor_size = 0.2
target_size = 0.3
home_size = 0.4
home_range_size = home_size * 7
fs = 500
timeLimit = 30

# 0 deg rotation matrix to be used between trials (i.e. finding home)
no_rot = lib.make_rot_mat(0)

# Create NI channels
# Inputs
input_task = nidaqmx.Task()
input_task.ai_channels.add_ai_voltage_chan("Dev1/ai0", min_val=0, max_val=5)
input_task.ai_channels.add_ai_voltage_chan("Dev1/ai1", min_val=0, max_val=5)
input_task.timing.cfg_samp_clk_timing(
    fs, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS
)

## Psychopy set up
# Create window
win = visual.Window(
    fullscr=True,
    monitor="testMonitor",
    units="pix",
    color="black",
    waitBlanking=False,
    screen=1,
    size=[1920, 1080],
)

# set up clocks
timer = core.Clock()

int_cursor = visual.Circle(win, radius=lib.cm_to_pixel(cursor_size), fillColor="white")
arc = visual.Circle(win, radius=lib.cm_to_pixel(7), lineColor="blue", fillColor=None, edges=200)
home = visual.Circle(
    win, radius=lib.cm_to_pixel(home_size), lineColor="red", fillColor=None
)
input_task.start()
while timer.getTime() < timeLimit:
    arc.draw()
    pot_data = lib.get_xy(input_task)
    current_pos = [lib.x_volt_to_pixel(pot_data[0]), lib.y_volt_to_pixel(pot_data[1])]
    lib.set_position(current_pos, int_cursor, no_rot)
    home.draw()
    win.flip()

input_task.stop()
input_task.close()