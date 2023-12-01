import nidaqmx
from psychopy import core

# 1 for vib 1, 2 for vib 2, 3 for both
vibration = 3

vib_off = [False, False] # Flexors and Extensors off
both_vib_on = [True, True] # Flexors and Extensors on
vib1_on = [True, False] # Extensor on
vib2_on = [False, True] # Flexor on

# Outputs - have to create separate tasks for input/output
output_task = nidaqmx.Task()
output_task.do_channels.add_do_chan("Dev1/port0/line0") # Extensor
output_task.do_channels.add_do_chan("Dev1/port0/line1") # Flexor
print("DAQ set up")

if vibration == 1:
    output_task.write(vib1_on)
elif vibration == 2:
    output_task.write(vib2_on)
elif vibration == 3:
    output_task.write(both_vib_on)
else:
    output_task.write(vib_off)


timer = core.Clock()
timer.reset()
print("Vibration on")
while timer.getTime() < 2:
    continue
output_task.write(vib_off)
print("Vibration off")

output_task.stop()
output_task.close()

