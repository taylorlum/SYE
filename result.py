import pandas as pd
import numpy as np
import requests
import pyreadr
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri

# Enable conversion between R and Pandas
pandas2ri.activate()

# Load RDS Model from GitHub
tie_reg_url = "https://raw.githubusercontent.com/taylorlum/SYE/main/tie_reg.rds"
rds_path = "tie_reg.rds"

# Download the RDS file
response = requests.get(tie_reg_url)
with open(rds_path, "wb") as f:
    f.write(response.content)

# Read the RDS model
r_model = pyreadr.read_r(rds_path)  # This gives a dictionary-like object
tie_reg = r_model[None]  # Extract model object

# Read tie_2324.csv from GitHub
tie_2324_url = "https://raw.githubusercontent.com/taylorlum/SYE/main/tie_2324.csv"
tie_2324 = pd.read_csv(tie_2324_url)

# Convert Pandas DataFrame to R DataFrame
tie_2324_r = pandas2ri.py2rpy(tie_2324)

# Predict tie probability using the R model
ro.globalenv["tie_reg"] = tie_reg
ro.globalenv["tie_2324_r"] = tie_2324_r
ro.r('tie_2324_r$Tie_Prob <- predict(tie_reg, newdata = tie_2324_r, type = "response")')

# Convert back to Pandas DataFrame
tie_2324_pred = pandas2ri.rpy2py(ro.globalenv["tie_2324_r"])

# Elo probability function in Python
def logistic_elo_probs(home_elo, away_elo):
    home_adjusted_elo = home_elo + 15
    elo_diff = away_elo - home_adjusted_elo
    prob_home_win = 1 / (1 + 10**(elo_diff / 400))
    prob_away_win = 1 - prob_home_win
    return prob_home_win, prob_away_win

# Compute probabilities
tie_2324_pred["home_win_prob"] = np.nan
tie_2324_pred["visitor_win_prob"] = np.nan

for index, row in tie_2324_pred.iterrows():
    home_prob, away_prob = logistic_elo_probs(row["Home_Elo_Before"], row["Visitor_Elo_Before"])
    tie_prob = row["Tie_Prob"] / 2
    tie_2324_pred.at[index, "home_win_prob"] = home_prob - tie_prob
    tie_2324_pred.at[index, "visitor_win_prob"] = away_prob - tie_prob

# Save final output as CSV
output_path = "data/sched_2324_diff.csv"
tie_2324_pred.to_csv(output_path, index=False)
