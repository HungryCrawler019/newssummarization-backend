import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup


load_dotenv()
api_key = os.getenv("NY_API_KEY")


def getLatestNews():
    url = 'https://api.nytimes.com/svc/topstories/v2/home.json'
    params = {
        'api-key': api_key
    }
    response = requests.get(url, params=params)
    data = response.json()
    # Get the first 5 stories
    latest_five_stories = data['results'][:5]
    return latest_five_stories

def scrapeNewsContent(url: str):
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the section with the specified class name (replace with actual class name if needed)
        article_body = soup.find('section', {'class': 'meteredContent css-1r7ky0e'})
        
        # Check if the element was found
        if article_body:
            # Extract and print the text
            text = article_body.get_text(separator=' ', strip=True)
            print(text)
        else:
            print('Article body not found.')
    else:
        print('Failed to retrieve the webpage.')
