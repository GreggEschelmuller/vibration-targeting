"""
This file contains a series of functions used for a wrist-based cursor control experiment.
The experiment is coded in psychopy. The functions and code were written by Gregg Eschelmuller.
"""

import numpy as np
import pandas as pd
import nidaqmx


def configure_input(fs):
    input_task = nidaqmx.Task()
    input_task.ai_channels.add_ai_voltage_chan("Dev1/ai0", min_val=0, max_val=5)
    input_task.ai_channels.add_ai_voltage_chan("Dev1/ai1", min_val=0, max_val=5)
    input_task.timing.cfg_samp_clk_timing(
        fs, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS
    )
    return input_task

def configure_output():
    # Outputs - have to create separate tasks for input/output
    output_task = nidaqmx.Task()
    output_task.do_channels.add_do_chan("Dev1/port0/line0") # Extensor
    output_task.do_channels.add_do_chan("Dev1/port0/line1") # Flexor
    return output_task

def generate_trial_dict():
    template = {
        "trial_num": [],
        "move_times": [],
        "wrist_x_end": [],
        "wrist_y_end": [],
        "curs_x_end": [],
        "curs_y_end": [],
        "end_angles": [],
        "block": [],
        "target_angle": [],
        'rt': [],
    }
    return template

def generate_position_dict():
    template = {
        "x_volts": [],
        "y_volts": [],
        "wrist_x": [],
        "wrist_y": [],
        "curs_x": [],
        "curs_y": [],
        "time": [],
        "move_index": [],
    }
    return template

# 24 inch diag - resololution 1920x1080
def cm_to_pixel(cm):
    return cm * 36.14


def pixel_to_cm(pix):
    return pix / 36.24

def x_volt_to_pixel(volt):
    pix = (volt - 2.4) * 620
    return pix

def y_volt_to_pixel(volt):
    pix = (volt - 2.4) * 620
    return pix

def read_trial_data(file_name, sheet=0):
    # Reads in the trial data from the excel file
    return pd.read_excel(file_name, sheet_name=sheet, engine="openpyxl")


def make_rot_mat(theta):
    return np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])


def exp_filt(pos0, pos1, alpha=0.5):
    x = (pos0[0] * alpha) + (pos1[0] * (1 - alpha))
    y = (pos0[1] * alpha) + (pos1[1] * (1 - alpha))
    return [x, y]

def get_xy(task):
    while True:
        vals = task.read(
            number_of_samples_per_channel=nidaqmx.constants.READ_ALL_AVAILABLE
        )
        if len(vals[0]) == 0:
            continue
        else:
            x_data = vals[0]
            y_data = vals[1]
        return [x_data[-1], y_data[-1]] 



# Turned into two separate functions
# def get_xy(task):
#     while True:
#         vals = task.read(
#             number_of_samples_per_channel=nidaqmx.constants.READ_ALL_AVAILABLE
#         )
#         if vals == None:
#             continue
#         elif not vals == None:
#             x_data = vals[0]
#             y_data = vals[1]

#             # If buffer contains multiple data points take the lastest one
#             if len(x_data) > 1:
#                 x_data = [x_data[-1]]
#             if len(y_data) > 1:
#                 y_data = [y_data[-1]]

#             # I don't remember why this check is here, but it doesn't work without it
#             if not len(vals[0]) == 0:
#                 # Offset cursor to middle position
#                 x = x_data[0] - 2.2
#                 y = y_data[0] - 2.2

#                 # Cursor gain
#                 x *= 550
#                 y *= 550
#                return [x, y]


def contains(small_circ, large_circ):
    d = np.sqrt(
        (small_circ.pos[0] - large_circ.pos[0]) ** 2
        + (small_circ.pos[1] - large_circ.pos[1]) ** 2
    )
    return (d + small_circ.radius) < large_circ.radius


def set_position(pos, circ, rot_mat=make_rot_mat(0)):
    circ.pos = np.matmul(rot_mat, pos)
    circ.draw()


def calc_target_pos(angle, amp=8):
    # Calculates the target position based on the angle and amplitude
    magnitude = cm_to_pixel(amp)
    x = np.cos(angle * (np.pi / 180)) * magnitude
    y = np.sin(angle * (np.pi / 180)) * magnitude
    return x, y


def calc_amplitude(pos):
    # Calculates the amplitude of the cursor relative to middle
    amp = np.sqrt(np.dot(pos, pos))
    return amp
