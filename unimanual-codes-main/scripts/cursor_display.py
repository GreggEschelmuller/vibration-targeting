# Simple psycopy script to display cursor
from psychopy import visual, core
import helper_functions as hf
import nidaqmx

cursor_size = 0.075
target_size = 0.5
home_size = 0.15
home_range_size = home_size * 5
fs = 500
time_limit = 10


input_task = nidaqmx.Task()
input_task.ai_channels.add_ai_voltage_chan("Dev1/ai0", min_val=0, max_val=5)
input_task.ai_channels.add_ai_voltage_chan("Dev1/ai2", min_val=0, max_val=5)
input_task.timing.cfg_samp_clk_timing(
    fs, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS
)

win = visual.Window(
    units="pix",
    color="black",
    waitBlanking=False,
    screen=1,
    fullscr=True,
    size=(1920, 1080)
)

int_cursor = visual.Rect(
    win, width=hf.cm_to_pixel(cursor_size), height=hf.cm_to_pixel(20), fillColor="green"
)

input_task.start()

move_clock = core.Clock()
move_clock.reset()
position = []
position.append(hf.get_x(input_task))
# Starting collection
print("Starting Collection")
while move_clock.getTime() < time_limit:
    cursor_pos = hf.get_x(input_task)
    position.append(cursor_pos)
    current_position = hf.exp_filt(position[-2], position[-1], 0.5)
    hf.set_position(current_position, int_cursor)
    win.flip()

input_task.stop()
input_task.close()
print("Done Collection")