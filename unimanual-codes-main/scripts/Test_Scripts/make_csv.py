import pandas as pd

trial_summary_data = {
    "trial_num": [],
    "target_amp": [],
    "full_feedback": [],
    "terminal_feedback": [],
    "offset": [],
    "offset_direction": [],
    "offset_size": [],
    "clamp_direction": [],
    "clamp": [],
    "clamp_angle": [],
    "vibration": [],
    "move_times": [],
    "elbow_end": [],
    "curs_end": [],
    "error": [],
}

# For online position data
position_data = {
    "elbow_pos": [],
    "time": [],
}

pd.DataFrame(trial_summary_data).to_csv("trial_data.csv", index=False)
pd.DataFrame(position_data).to_csv("position_data.csv", index=False)
