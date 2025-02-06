import requests
from bs4 import BeautifulSoup

# URL of the website to scrape
url = 'https://saintsathletics.com/sports/womens-ice-hockey'  # Replace with the URL you want to scrape

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all the anchor tags in the webpage (links)
    links = soup.find_all('a')

    # Open a file to write the links
    with open('scraped_links.txt', 'w') as file:
        for link in links:
            href = link.get('href')
            if href:
                file.write(href + '\n')

    print("Scraping completed! Links saved in 'scraped_links.txt'")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
