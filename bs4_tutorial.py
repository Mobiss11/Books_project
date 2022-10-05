import requests
from bs4 import BeautifulSoup

url = 'https://www.franksonnenbergonline.com/blog/are-you-grateful/'
response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'lxml')

title_tag = soup.find('main').find('header').find('h1')
print(title_tag.text)

image = soup.find('img', class_='attachment-post-image')['src']
print(image)

description = soup.find('div', class_='entry-content')
print(description.text)

