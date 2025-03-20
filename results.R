url <- "https://raw.githubusercontent.com/taylorlum/SYE/main/tie_reg.rds"
temp <- tempfile(fileext = ".rds")
download.file(url, temp, mode = "wb")
tie_reg <- readRDS(temp)
unlink(temp)

library(readr)
tie_2324 <- read_csv("https://raw.githubusercontent.com/taylorlum/SYE/main/tie_2324.csv")

logistic_elo_probs <- function(home_elo, away_elo) {
  # Adjust Elo for home advantage
  home_adjusted_elo <- home_elo + 15
  elo_diff = away_elo - home_adjusted_elo
  
  # Calculate probabilities
  prob_home_win <- 1 / (1 + 10^((elo_diff) / 400))
  prob_away_win <- 1 - prob_home_win
  
  tie_prob = predict(tie_reg, newdata = data.frame(Elo_Diff = abs(elo_diff)), type = "response")
  
  # Return probabilities
  list(
    home_win_prob = prob_home_win - (tie_prob / 2),
    away_win_prob = prob_away_win - (tie_prob / 2),
    tie_prob = tie_prob
  )
}

# Make predictions
tie_2324_pred <- tie_2324
tie_2324_pred$Tie_Prob <- predict(tie_reg, newdata = tie_2324, type = "response")

sched_2324_diff <- tie_2324_pred %>% select(c(1:7, 11, 12))

options(scipen = 999)

# Initialize probability columns
sched_2324_diff$home_win_prob <- NA
sched_2324_diff$visitor_win_prob <- NA
sched_2324_diff$tie_prob <- NA

# Compute probabilities row by row
for (row in 1:nrow(sched_2324_diff)) {
  probs <- logistic_elo_probs(
    sched_2324_diff$Home_Elo_Before[row], 
    sched_2324_diff$Visitor_Elo_Before[row]
  )
  sched_2324_diff$home_win_prob[row] <- probs$home_win_prob
  sched_2324_diff$visitor_win_prob[row] <- probs$away_win_prob
  sched_2324_diff$tie_prob[row] <- probs$tie_prob
}

# Save the output
write_csv(sched_2324_diff, "sched_2324_diff.csv")