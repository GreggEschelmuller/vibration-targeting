import pickle

# Dictionary for end point data for whole block - will be used to generate excel
template_data_dict = {
    "move_times": [],
    "elbow_end": [],
    "curs_end": [],
    "target_pos": [],
    "rotation": [],
    "vibration": [],
}

# Template to store data for each trial
template_trial_dict = {
    "move_times": [],
    "elbow_end": [],
    "curs_end": [],
    "target_pos": [],
    "rotation": [],
    "vibration": [],
    "curs_pos": [],
    "elbow_pos": [],
    "time": [],
    "velocity": [],
}

with open('template_data_dict.pkl', 'wb') as f:
    pickle.dump(template_data_dict, f)

with open('template_trial_dict.pkl', 'wb') as f:
    pickle.dump(template_trial_dict, f)