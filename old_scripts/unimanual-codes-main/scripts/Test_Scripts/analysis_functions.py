import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def calculate_error_difference(df):
    avg_error_no_vibration = df[df['vibration'] == 0]['error'].mean()
    avg_error_with_vibration = df[df['vibration'] == 1]['error'].mean()
    error_diff = avg_error_with_vibration - avg_error_no_vibration
    return avg_error_no_vibration, avg_error_with_vibration, error_diff

def plot_block_data(df, block_name):
    plt.scatter(df['trial'][df['vibration'] == 0], df['error'][df['vibration'] == 0], label='No Vibration', marker='o')
    plt.scatter(df['trial'][df['vibration'] == 1], df['error'][df['vibration'] == 1], label='Vibration', marker='x')
    plt.title(f'{block_name} Block')
    plt.xlabel('Trial')
    plt.ylabel('Error Score')
    plt.legend()
    plt.grid(True)
    
def calculate_avg_error(df):
    return df['error'].mean()

# Simulating some sample data for demonstration
np.random.seed(0)
n_trials = 100  # Number of trials in each block

# Simulating baseline data
baseline_data = {
    'trial': np.arange(1, n_trials + 1),
    'error': np.random.normal(0, 1, n_trials),  # Randomly generated error scores
    'vibration': np.random.choice([0, 1], n_trials)  # Randomly introducing vibration
}
baseline_df = pd.DataFrame(baseline_data)

# Simulating exposure data
exposure_data = {
    'trial': np.arange(1, n_trials + 1),
    'error': np.random.normal(0.5, 1, n_trials),  # Slightly shifted error to simulate exposure effect
    'vibration': np.random.choice([0, 1], n_trials)
}
exposure_df = pd.DataFrame(exposure_data)

# Simulating post-exposure data
post_exposure_data = {
    'trial': np.arange(1, n_trials + 1),
    'error': np.random.normal(0, 1, n_trials),
    'vibration': np.random.choice([0, 1], n_trials)
}
post_exposure_df = pd.DataFrame(post_exposure_data)

# Displaying the first few rows of each dataframe
baseline_df.head(), exposure_df.head(), post_exposure_df.head()


# Function to plot data for each block
def plot_block_data(df, block_name):
    plt.scatter(df['trial'][df['vibration'] == 0], df['error'][df['vibration'] == 0], label='No Vibration', marker='o')
    plt.scatter(df['trial'][df['vibration'] == 1], df['error'][df['vibration'] == 1], label='Vibration', marker='x')
    plt.title(f'{block_name} Block')
    plt.xlabel('Trial')
    plt.ylabel('Error Score')
    plt.legend()
    plt.grid(True)

# Creating subplots
plt.figure(figsize=(15, 5))

# Plotting Baseline Data
plt.subplot(1, 3, 1)
plot_block_data(baseline_data, 'Baseline')

# Plotting Exposure Data
plt.subplot(1, 3, 2)
plot_block_data(exposure_data, 'Exposure')

# Plotting Post-Exposure Data
plt.subplot(1, 3, 3)
plot_block_data(post_exposure_data, 'Post-Exposure')

plt.tight_layout()
plt.show()
