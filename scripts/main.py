from psychopy import visual, core
import numpy as np
import pandas as pd
import helper_functions as hf
import pickle
from datetime import datetime
import copy
import os
import nidaqmx

# TO DO
# - code in error into excel writing

# ------------------Blocks to run ------------------
# Use this to run whole protocol
# make sure the strings match the names of the sheets in the excel
# ExpBlocks = [
#     "Practice",
#     "Baseline",
#     "Exposure",
#     "Post"
#     ]

# For testing a few trials
ExpBlocks = ["Testing"]
# ExpBlocks = ["Practice"]

# ----------- Participant info ----------------

# For clamp and rotation direction
rot_direction = 1  # 1 for forwrad, -1 for backward
participant = 99


study_id = "Wrist Visuomotor Rotation"
experimenter = "Gregg"
current_date = datetime.now()
date_time_str = current_date.strftime("%Y-%m-%d %H:%M:%S")


study_info = {
    "Participant ID": participant,
    "Date_Time": date_time_str,
    "Study ID": study_id,
    "Experimenter": experimenter,
}
# experiment_info = pd.DataFrame.from_dict(study_info)

if not participant == 99:
    print(study_info)
    input(
        """
        Make sure changed the participant info is correct before continuing.
        Press enter to continue.
        """
    )

# # Check if directory exists and if it is empty
dir_path = "data/P" + str(participant)

if not participant == 99:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(
            """
        Directory didn't exist so one was created. Continuing with program.
        """
        )
    elif len(os.listdir(dir_path)) == 0:
        print(
            """
        Directory already exists and is empty. Continuing with program."""
        )
    elif os.path.exists(dir_path) and not len(dir_path) == 0:
        print(
            """
        This directory exists and isn't empty, exiting program.
        Please check the contents of the directory before continuing.
        """
        )
        exit()

# set up file path
file_path = f"data/P{str(participant)}/p{str(participant)}"
# experiment_info.to_csv(file_path + "_studyinfo.csv")

print("Setting everything up...")

# ------------------------ Set up --------------------------------

# Variables set up
cursor_size = 0.075
target_size = 0.1
home_size = 0.15
home_range_size = home_size * 5
fs = 500
timeLimit = 2

# 0 deg rotation matrix to be used between trials (i.e. finding home)
no_rot = hf.make_rot_mat(0)

# Create NI channels
# Inputs
input_task = nidaqmx.Task()
input_task.ai_channels.add_ai_voltage_chan("Dev1/ai0", min_val=0, max_val=5)
input_task.ai_channels.add_ai_voltage_chan("Dev1/ai1", min_val=0, max_val=5)
input_task.timing.cfg_samp_clk_timing(
    fs, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS
)

# Outputs - have to create separate tasks for input/output
output_task = nidaqmx.Task()
output_task.do_channels.add_do_chan("Dev1/port0/line0") # Extensor
output_task.do_channels.add_do_chan("Dev1/port0/line1") # Flexor


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
move_clock = core.Clock()
home_clock = core.Clock()
pre_trial_clock = core.Clock()

home = visual.Circle(
    win, radius=hf.cm_to_pixel(home_size), lineColor="red", fillColor=None
)

home_range = visual.Circle(win, radius=hf.cm_to_pixel(home_range_size), lineColor=None)

int_cursor = visual.Circle(win, radius=hf.cm_to_pixel(cursor_size), fillColor="Black")

target = visual.Circle(win, radius=hf.cm_to_pixel(target_size), fillColor="green")

# Data dicts for storing data
trial_summary_data_template = {
    "trial_num": [],
    "move_times": [],
    "wrist_x_end": [],
    "wrist_y_end": [],
    "curs_x_end": [],
    "curs_y_end": [],
    "end_angles": [],
    "block": [],
}

# For online position data
position_data_template = {
    "wrist_x": [],
    "wrist_y": [],
    "time": [],
}

print("Done set up")

# -------------- start main experiment loop ------------------------------------
input("Press enter to continue to first block ... ")
for block in range(len(ExpBlocks)):
    condition = hf.read_trial_data("Trials.xlsx", ExpBlocks[block])

    # Summary data dictionaries for this block
    block_data = copy.deepcopy(trial_summary_data_template)
    file_ext = ExpBlocks[block]

    # starts NI DAQ task for data collection and output
    input_task.start()
    output_task.start()

    for i in range(len(condition.trial_num)):
        # Creates dictionary for single trial
        current_trial = copy.deepcopy(trial_summary_data_template)
        position_data = copy.deepcopy(position_data_template)

        full_feedback = condition.full_feedback[i]
        terminal_feedback = condition.terminal_feedback[i]  # Load this from the excel
        vibration = condition.vibration[i]
        trial_type = condition.trial_type[i]
        current_target_pos = hf.calc_target_pos(
            condition.target_pos[i], condition.target_amp[i]
        )

        # Set up vibration output
        if condition.vibration[i] == 0:
            vib_output = [False, False] # Flexors and Extensors off
        elif condition.vibration[i] == 1:
            vib_output = [True, True] # Flexors and Extensors on
        elif condition.vibration[i] == 2:
            vib_output = [True, False] # Extensor on
        elif condition.vibration[i] == 3:
            vib_output = [False, True] # Flexor on

        rotation = condition.rotation[i]
        clamp = condition.clamp[i]

        if rotation:
            rot_mat = hf.make_rot_mat(
                np.radians(condition.rotation_angle[i] * rot_direction)
            )
        else:
            rot_mat = hf.make_rot_mat(0)

        home.draw()
        int_cursor.color = None
        int_cursor.draw()
        win.flip()

        # Checks if cursor is close to home and turns it white
        in_range = False
        current_pos = hf.get_xy(input_task)
        int_cursor.pos = current_pos
        while not in_range:
            if hf.contains(int_cursor, home_range):
                in_range = True
                int_cursor.color = "white"
                int_cursor.draw()
                win.flip()
            current_pos = hf.get_xy(input_task)
            hf.set_position(current_pos, int_cursor, no_rot)
            home.draw()
            win.flip()

        # Checks if cursor is in home position
        is_home = False
        while not is_home:
            prev_pos = int_cursor.pos
            if hf.contains(int_cursor, home):
                home_clock.reset()
                while True:
                    current_pos = hf.get_xy(input_task)
                    home.draw()
                    hf.set_position(current_pos, int_cursor, no_rot)
                    win.flip()

                    if home_clock.getTime() > 0.5:
                        is_home = True
                        break
                    if not hf.contains(int_cursor, home):
                        break

            current_pos = hf.get_xy(input_task)
            home.draw()
            hf.set_position(current_pos, int_cursor, no_rot)
            win.flip()

        hf.set_position(current_target_pos, target, no_rot)
        pre_trial_clock.reset()
        while hf.contains(int_cursor, home):
            current_pos = hf.get_xy(input_task)
            home.draw()
            hf.set_position(current_pos, int_cursor, rot_mat)

            target.draw()
            win.flip()
            position_data["wrist_x"].append(current_pos[0])
            position_data["wrist_y"].append(current_pos[1])
            position_data["time"].append([pre_trial_clock.getTime()])

        if not condition.full_feedback[i]:
            int_cursor.color = None

        # Start vibration
        output_task.write(vib_output)

        # run trial until time limit is reached or target is reached
        move_clock.reset()
        while move_clock.getTime() < timeLimit:
            # Run trial
            current_time = move_clock.getTime()
            current_pos = hf.get_xy(input_task)
            target.draw()
            hf.set_position(current_pos, int_cursor)
            win.flip()

            # Save position data
            position_data["wrist_x"].append(current_pos[0])
            position_data["wrist_y"].append(current_pos[1])
            position_data["time"].append(current_time)

            if hf.calc_amplitude(current_pos) >= hf.cm_to_pixel(
                condition.target_amp[i]
            ):
                output_task.write([False, False])
                # Show terminal feedback
                if condition.terminal_feedback[i]:
                    int_cursor.color = "White"
                    int_cursor.draw()
                    target.draw()
                    win.flip()

                # break trial loop
                break
        output_task.write([False, False])
        # Leave current window for 200ms
        core.wait(0.2, hogCPUperiod=0.2)
        int_cursor.color = None
        int_cursor.draw()
        win.flip()

        # Print trial information
        print(f"Trial {i+1} done.")
        print(f"Movement time: {round((current_time*1000),1)} ms")
        print(
            f"Target position: {condition.target_pos[i]}     Cursor Position: {round(np.degrees(np.arctan2(int_cursor.pos[1], int_cursor.pos[0])), 2)}"
        )

        print(" ")

        # append trial file
        current_trial["move_times"].append(current_time)
        current_trial["wrist_x_end"].append(hf.pixel_to_cm(current_pos[0]))
        current_trial["wrist_y_end"].append(hf.pixel_to_cm(current_pos[1]))
        current_trial["curs_x_end"].append(hf.pixel_to_cm(int_cursor.pos[0]))
        current_trial["curs_y_end"].append(hf.pixel_to_cm(int_cursor.pos[1]))
        current_trial["end_angles"].append(
            np.degrees(np.arctan2(int_cursor.pos[1], int_cursor.pos[0]))
        )
        current_trial["trial_num"].append(i + 1)
        current_trial["block"].append(ExpBlocks[block])

        # append block data
        block_data["move_times"].append(current_time)
        block_data["wrist_x_end"].append(hf.pixel_to_cm(current_pos[0]))
        block_data["wrist_y_end"].append(hf.pixel_to_cm(current_pos[1]))
        block_data["curs_x_end"].append(hf.pixel_to_cm(int_cursor.pos[0]))
        block_data["curs_y_end"].append(hf.pixel_to_cm(int_cursor.pos[1]))
        block_data["end_angles"].append(
            np.degrees(np.arctan2(int_cursor.pos[1], int_cursor.pos[0]))
        )
        block_data["trial_num"].append(i + 1)
        block_data["block"].append(ExpBlocks[block])

        pd.DataFrame.from_dict(current_trial).to_csv(
            f"{file_path}_trial_{str(i+1)}_{file_ext}.csv", index=False
        )
        pd.DataFrame.from_dict(position_data).to_csv(
            f"{file_path}_position_{str(i+1)}_{file_ext}.csv", index=False
        )


        del current_trial, position_data

    # End of bock saving
    print("Saving Data")
    trial_data = pd.merge(
        pd.DataFrame.from_dict(block_data),
        pd.DataFrame.from_dict(condition),
        on="trial_num",
    )

    trial_data.to_csv(file_path + "_" + file_ext + ".csv", index=False)

    print("Data Succesfully Saved")

    del condition, trial_data, block_data
    input_task.stop()
    output_task.stop()
    input("Press enter to continue to next block ... ")

input_task.close()
output_task.close()
print("Experiment Done")
