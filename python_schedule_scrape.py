import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def scrape_results_function(date):
    date_code = date.strftime('%Y%m%d')
    url = f"https://www.collegehockeynews.com/women/schedule.php?date={date_code}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    table = soup.find('table')
    if table is None:
        return pd.DataFrame()
    
    df = pd.read_html(str(table))[0]
    return clean_sched_function(df)

def clean_sched_function(df):
    df = df.iloc[:, [0, 1, 3, 4, 5]]  # Select columns
    df.columns = ['Visitor', 'Visitor_Score', 'Home', 'Home_Score', 'OT']

    df = df[df['Home'].notna() & (df['Home'].str.strip() != '')] 
    df['Date_string'] = df['Visitor'].where(df['Visitor'].str.match(r'^[A-Za-z]+, [A-Za-z]+ \d{1,2}, \d{4}$'))
    df['Date_string'] = df['Date_string'].fillna(method='ffill')
    df = df.dropna(subset=['Date_string'])
    
    df['Date'] = pd.to_datetime(df['Date_string'], format='%A, %B %d, %Y')
    df['Division'] = df['Visitor'].where(df['Visitor'] == df['Visitor_Score'])
    df['Division'] = df['Division'].fillna(method='ffill')
    
    df = df[(df['Visitor'] != df['Visitor_Score']) & (df['Division'] != 'Exhibition')]
    df = df.drop(columns=['Date_string'])
    #df['OT'] = df['OT'].apply(lambda x: 0 if x == '' else 1)
    
    return df[['Date', 'Visitor', 'Visitor_Score', 'Home', 'Home_Score', 'OT', 'Division']]

def main():
    start_date = datetime(2024, 9, 28)
    end_date = datetime(2025, 3, 31)
    dates = [start_date + timedelta(days=i) for i in range(0, (end_date - start_date).days + 1, 8)]
    
    schedule = scrape_results_function(datetime(2024, 9, 20))
    for date in dates:
        temp = scrape_results_function(date)
        schedule = pd.concat([schedule, temp], ignore_index=True)
    
    schedule.to_csv('schedule_2425.csv', index=False)

if __name__ == "__main__":
    main()
