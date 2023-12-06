import pandas as pd
participant = 1
condition = "Testing"
trial_num=1
file_path = f"data/P{participant}/p{participant}_trial_{trial_num}_{condition}"

data = pd.read_csv(file_path)
print(data)
