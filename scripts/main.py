from psychopy import visual, core
import numpy as np
import pandas as pd
import src.lib as lib
# import pickle
from datetime import datetime
import copy
import os
import nidaqmx

# TO DO
# - code in error into excel writing

# CHANGE FOR PARTICIPANT
participant = 98

break_trials = 60

# ------------------Blocks to run -------------------------------------------------
# Use this to run whole protocol
# make sure the strings match the names of the sheets in the excel
# ExpBlocks = ["Practice"]

# ExpBlocks = [
#     "Baseline",
#     "Testing",
#     ]


# For piloting
ExpBlocks = ["piloting"]

# ----------- Participant info -------------------------------------------------

# For clamp and rotation direction
rot_direction = 1  # 1 for forwrad, -1 for backward

# # Check if directory exists and if it is empty
dir_path = "data/P" + str(participant)

if ExpBlocks[0] == "Practice":
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
        ans = input(
            """
        This directory exists and isn't empty.
        Do you want to continue? (y/n)
        """
        )
        if ans.lower() == "n":
            print("Exiting program")
            exit()
        elif ans.lower() == 'y':
            print("Continuing with program")
        else:
            print("Invalid input, exiting program")

# set up file path
file_path = f"data/P{str(participant)}/p{str(participant)}"

print("Setting everything up...")

# ------------------------ Set up --------------------------------

# Variables set up
cursor_size = 0.2
target_size = 0.3
home_size = 0.4
home_range_size = home_size * 7
fs = 500
timeLimit = 2

# 0 deg rotation matrix to be used between trials (i.e. finding home)
no_rot = lib.make_rot_mat(0)

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
home_clock = core.Clock()
trial_clock = core.Clock()
display_clock = core.Clock()

home = visual.Circle(
    win, radius=lib.cm_to_pixel(home_size), lineColor="red", fillColor=None
)

home_range = visual.Circle(win, radius=lib.cm_to_pixel(home_range_size), lineColor=None)
int_cursor = visual.Circle(win, radius=lib.cm_to_pixel(cursor_size), fillColor="Black")
target = visual.Circle(win, radius=lib.cm_to_pixel(target_size), fillColor="green")

print("Done set up")

# -------------- start main experiment loop ------------------------------------
input("Press enter to continue to first block ... ")
for block in range(len(ExpBlocks)):
    condition = lib.read_trial_data("Trials.xlsx", ExpBlocks[block])

    # Summary data dictionaries for this block
    block_data = lib.generate_trial_dict()
    file_ext = ExpBlocks[block]



    for i in range(len(condition.trial_num)):
        if np.isnan(condition.trial_num[i]):
            break
        print(condition.trial_num[i])
        # Creates dictionary for single trial
        current_trial = lib.generate_trial_dict()
        position_data = lib.generate_position_dict()

        full_feedback = condition.full_feedback[i]
        terminal_feedback = condition.terminal_feedback[i]  # Load this from the excel
        vibration = condition.vibration[i]
        trial_type = condition.trial_type[i]

        # Jitters side targets only
        if condition.target_pos[i] == 90:
            target_angle  = condition.target_pos[i]
            current_target_pos = lib.calc_target_pos(
            target_angle, condition.target_amp[i]
            )
        else:
            target_angle = condition.target_pos[i] + np.random.randint(-10,10)
            current_target_pos = lib.calc_target_pos(
            target_angle, condition.target_amp[i]
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
            rot_mat = lib.make_rot_mat(
                np.radians(condition.rotation_angle[i] * rot_direction)
            )
        else:
            rot_mat = lib.make_rot_mat(0)

        home.draw()
        int_cursor.color = None
        int_cursor.draw()
        win.flip()

        input_task = lib.configure_input(fs)
        output_task = lib.configure_output()

        # starts NI DAQ task for data collection and output
        input_task.start()
        output_task.start()

        # Checks if cursor is close to home and turns it white
        in_range = False
        pot_data = lib.get_xy(input_task)
        current_pos = [lib.x_volt_to_pixel(pot_data[0]), lib.y_volt_to_pixel(pot_data[1])]
        int_cursor.pos = current_pos
        while not in_range:
            if lib.contains(int_cursor, home_range):
                in_range = True
                int_cursor.color = "white"
                int_cursor.draw()
                win.flip()
            pot_data = lib.get_xy(input_task)
            current_pos = [lib.x_volt_to_pixel(pot_data[0]), lib.y_volt_to_pixel(pot_data[1])]
            lib.set_position(current_pos, int_cursor, no_rot)
            home.draw()
            win.flip()

        # Checks if cursor is in home position
        is_home = False
        while not is_home:
            prev_pos = int_cursor.pos
            if lib.contains(int_cursor, home):
                home_clock.reset()
                while True:
                    pot_data = lib.get_xy(input_task)
                    current_pos = [lib.x_volt_to_pixel(pot_data[0]), lib.y_volt_to_pixel(pot_data[1])]
                    home.draw()
                    lib.set_position(current_pos, int_cursor, no_rot)
                    win.flip()

                    if home_clock.getTime() > 0.5:
                        is_home = True
                        break
                    if not lib.contains(int_cursor, home):
                        break

            pot_data = lib.get_xy(input_task)
            current_pos = [lib.x_volt_to_pixel(pot_data[0]), lib.y_volt_to_pixel(pot_data[1])]
            home.draw()
            lib.set_position(current_pos, int_cursor, no_rot)
            win.flip()

        
        lib.set_position(current_target_pos, target, no_rot)
        trial_clock.reset()

        # Start vibration at target onset
        output_task.write(vib_output)
        while lib.contains(int_cursor, home):
            current_time = trial_clock.getTime()
            pot_data = lib.get_xy(input_task)
            current_pos = [lib.x_volt_to_pixel(pot_data[0]), lib.y_volt_to_pixel(pot_data[1])]
            home.draw()
            lib.set_position(current_pos, int_cursor, rot_mat)

            target.draw()
            win.flip()
            position_data['x_volts'].append(pot_data[0])
            position_data['y_volts'].append(pot_data[1])
            position_data["wrist_x"].append(current_pos[0])
            position_data["wrist_y"].append(current_pos[1])
            position_data["curs_x"].append(int_cursor.pos[0])
            position_data["curs_y"].append(int_cursor.pos[1])
            position_data["time"].append([trial_clock.getTime()])

        rt = trial_clock.getTime()

        if not condition.full_feedback[i]:
            int_cursor.color = None

        # run trial until time limit is reached or target is reached
        while trial_clock.getTime() < timeLimit:
            # Run trial
            current_time = trial_clock.getTime()
            pot_data = lib.get_xy(input_task)
            current_pos = [lib.x_volt_to_pixel(pot_data[0]), lib.y_volt_to_pixel(pot_data[1])]
            target.draw()
            lib.set_position(current_pos, int_cursor)
            win.flip()

            # Save position data
            position_data['x_volts'].append(pot_data[0])
            position_data['y_volts'].append(pot_data[1])
            position_data["wrist_x"].append(current_pos[0])
            position_data["wrist_y"].append(current_pos[1])
            position_data["curs_x"].append(int_cursor.pos[0])
            position_data["curs_y"].append(int_cursor.pos[1])
            position_data["time"].append([trial_clock.getTime()])

            if lib.calc_amplitude(current_pos) >= lib.cm_to_pixel(
                condition.target_amp[i]
            ):
                output_task.write([False, False])
                # Show terminal feedback
                if condition.terminal_feedback[i]:
                    int_cursor.color = "White"
                    target.draw()
                    int_cursor.draw()
                    win.flip()

                # break trial loop
                break
        # Leave current window for 300ms
        display_clock.reset()
        while display_clock.getTime() < 0.3:
            position_data['x_volts'].append(pot_data[0])
            position_data['y_volts'].append(pot_data[1])
            position_data["wrist_x"].append(current_pos[0])
            position_data["wrist_y"].append(current_pos[1])
            position_data["curs_x"].append(int_cursor.pos[0])
            position_data["curs_y"].append(int_cursor.pos[1])
            position_data["time"].append([trial_clock.getTime()])

        input_task.stop()
        output_task.stop()
        input_task.close()
        output_task.close()
        int_cursor.color = None
        int_cursor.draw()
        win.flip()
        # Print trial information
        print(f"Trial {i+1} done.")
        print(f"Movement time: {round(((current_time - rt)*1000),1)} ms")
        print(
            f"Target position: {target_angle}     Cursor Position: {round(np.degrees(np.arctan2(int_cursor.pos[1], int_cursor.pos[0])), 2)}"
        )

        print(" ")

        # append trial file
        current_trial["move_times"].append(current_time - rt)
        current_trial['rt'].append(rt)
        current_trial["wrist_x_end"].append(lib.pixel_to_cm(current_pos[0]))
        current_trial["wrist_y_end"].append(lib.pixel_to_cm(current_pos[1]))
        current_trial["curs_x_end"].append(lib.pixel_to_cm(int_cursor.pos[0]))
        current_trial["curs_y_end"].append(lib.pixel_to_cm(int_cursor.pos[1]))
        current_trial["end_angles"].append(
            np.degrees(np.arctan2(int_cursor.pos[1], int_cursor.pos[0]))
        )
        current_trial["trial_num"].append(i + 1)
        current_trial["block"].append(ExpBlocks[block])
        current_trial['target_angle'].append(target_angle)

        # append block data
        block_data["move_times"].append(current_time - rt)
        block_data['rt'].append(rt)
        block_data["wrist_x_end"].append(lib.pixel_to_cm(current_pos[0]))
        block_data["wrist_y_end"].append(lib.pixel_to_cm(current_pos[1]))
        block_data["curs_x_end"].append(lib.pixel_to_cm(int_cursor.pos[0]))
        block_data["curs_y_end"].append(lib.pixel_to_cm(int_cursor.pos[1]))
        block_data["end_angles"].append(
            np.degrees(np.arctan2(int_cursor.pos[1], int_cursor.pos[0]))
        )
        block_data["trial_num"].append(i + 1)
        block_data["block"].append(ExpBlocks[block])
        block_data['target_angle'].append(target_angle)

        pd.DataFrame.from_dict(current_trial).to_csv(
            f"{file_path}_trial_{str(i+1)}_{file_ext}.csv", index=False
        )
        
        pd.DataFrame.from_dict(position_data).to_csv(
            f"{file_path}_position_{str(i+1)}_{file_ext}.csv", index=False
        )

        del current_trial, position_data

        if (i+1) % break_trials == 0:
            input("Break before veridical trials - press enter to continue")

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
    input("Press enter to continue to next block ... ")
print("Experiment Done")
