import rpy2.robjects as ro
import pandas as pd
import requests

# Function to download the .rds model file from GitHub
def download_rds_file(url, save_path):
    response = requests.get(url)
    with open(save_path, 'wb') as f:
        f.write(response.content)

# Download the RDS file for the logistic regression model
rds_url = "https://raw.githubusercontent.com/taylorlum/SYE/main/tie_reg.rds"
rds_path = "tie_reg.rds"
download_rds_file(rds_url, rds_path)

# Load the RDS file using rpy2
ro.r['load'](rds_path)

# Assuming the RDS file contains a model named 'tie_reg'
tie_reg = ro.r['tie_reg']

# Load the CSV data from GitHub
csv_url = "https://raw.githubusercontent.com/taylorlum/SYE/main/tie_2324.csv"
tie_2324 = pd.read_csv(csv_url)

# Function to calculate probabilities based on Elo
def logistic_elo_probs(home_elo, away_elo):
    # Adjust Elo for home advantage
    home_adjusted_elo = home_elo + 15
    elo_diff = away_elo - home_adjusted_elo
    
    # Calculate probabilities
    prob_home_win = 1 / (1 + 10 ** (elo_diff / 400))
    prob_away_win = 1 - prob_home_win
    
    # Predict tie probabilities using the loaded R model
    tie_prob = tie_reg.rx2('predict')(ro.r['data.frame']({'Elo_Diff': abs(elo_diff)}), type="response")[0]
    
    # Return probabilities
    return {
        'home_win_prob': prob_home_win - (tie_prob / 2),
        'away_win_prob': prob_away_win - (tie_prob / 2),
        'tie_prob': tie_prob
    }

# Create a new column for the tie probabilities
tie_2324['Tie_Prob'] = tie_reg.rx2('predict')(ro.r['data.frame'](tie_2324), type="response")

# Select relevant columns from the dataframe
sched_2324_diff = tie_2324[['Home_Elo_Before', 'Visitor_Elo_Before', 'Tie_Prob']]

# Initialize new probability columns
sched_2324_diff['home_win_prob'] = None
sched_2324_diff['visitor_win_prob'] = None
sched_2324_diff['tie_prob'] = None

# Compute probabilities row by row
for idx, row in sched_2324_diff.iterrows():
    probs = logistic_elo_probs(
        row['Home_Elo_Before'], row['Visitor_Elo_Before']
    )
    sched_2324_diff.at[idx, 'home_win_prob'] = probs['home_win_prob']
    sched_2324_diff.at[idx, 'visitor_win_prob'] = probs['away_win_prob']
    sched_2324_diff.at[idx, 'tie_prob'] = probs['tie_prob']

# Save the final output to a CSV file
output_path = "sched_2324_diff.csv"
sched_2324_diff.to_csv(output_path, index=False)
