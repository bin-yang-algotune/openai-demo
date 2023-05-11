import requests
from bs4 import BeautifulSoup
from datetime import datetime

# URL to fetch
url = 'https://www.morningstar.com/news/marketwatch/20230419590/tesla-stock-falls-as-quarterly-revenue-misses-expectations-margins-drop'

# Send a GET request to the URL
response = requests.get(url)

# Parse the HTML content
soup = BeautifulSoup(response.content, 'html.parser')

# Find the datetime object within the HTML
date_time = soup.find('div', {'class': 'a-card-metadata__published'})

if date_time:
    # Extract the datetime from the datetime object
    publishing_date = datetime.strptime(date_time.text.strip(), '%b. %d, %Y %I:%M %p ET')
    print("Publishing date:", publishing_date)
else:
    print("Publishing date not found for", url)
