# Load required libraries
# install.packages("rvest", repos = "https://cloud.r-project.org")
# install.packages("tidyverse", repos = "https://cloud.r-project.org")

library(rvest)
library(tidyverse)

# Function to scrape schedule/results
scrape_results_function <- function(date) {
  date_code <- gsub("-", "", date)
  url <- paste0("https://www.collegehockeynews.com/women/schedule.php?date=", date_code)
  h <- read_html(url)
  tab <- h %>% html_nodes("table")
  obj <- tab %>% html_table()
  clean_sched <- clean_sched_function(obj[[1]])
  return(clean_sched)
}

# Function to clean the scraped table
clean_sched_function <- function(date_table) {
  date_table %>%
    select(1:6) %>%
    select(-X3) %>%
    rename(Visitor = X1, Visitor_Score = X2, Home = X4, Home_Score = X5, OT = X6) %>%
    mutate(Date_string = ifelse(grepl("[A-Za-z]+, [A-Za-z]+ \\d{1,2}, \\d{4}", Visitor), Visitor, NA)) %>%
    fill(Date_string, .direction = "down") %>%
    mutate(Date_string = ifelse(Visitor == "" & Visitor_Score == "", NA, Date_string)) %>%
    filter(!is.na(Date_string)) %>%
    mutate(Date = as.Date(Date_string, format = "%A, %B %d, %Y")) %>%
    mutate(Division = ifelse(Visitor == Visitor_Score & Visitor != "", Visitor, NA)) %>%
    mutate(Home_Score = as.integer(Home_Score), Visitor_Score = as.integer(Visitor_Score)) %>%
    fill(Division, .direction = "down") %>%
    filter(!if_all(everything(), is.na)) %>%
    filter(Visitor != Visitor_Score) %>%
    select(-c(Date_string)) %>%
    mutate(OT = if_else(OT == "", 0, 1)) %>%
    relocate(Date, .before = Visitor) %>%
    filter(Division != "Exhibition")
}

# Define the list of dates
dates_2425 <- seq(as.Date("2024-09-20"), as.Date("2025-03-31"), by = "week")

# Scrape and compile schedule data
sched_2425 <- scrape_results_function("2024-09-20")
for (week in dates_2425) {
  temp <- scrape_results_function(as.Date(week))
  sched_2425 <- rbind(sched_2425, temp)
}

# Save to CSV
write.csv(sched_2425, "schedule_2425.csv", row.names = FALSE)
