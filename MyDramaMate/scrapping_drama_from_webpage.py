import os 
from bs4 import BeautifulSoup
import requests
import csv
import html
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

# Function to scrape data from a given URL
def scrape_dramas(url):
    try:
        drama_html = requests.get(url, timeout=10).text
    except requests.exceptions.Timeout:
        print(f"Timeout occurred while trying to fetch data from {url}")
        return []

    soup = BeautifulSoup(drama_html, 'lxml')

    dramas = soup.find_all('div', class_='col-xs-9 row-cell content')

    results = []
    for drama in dramas:
        drama_title = drama.find('h6', class_='text-primary title').text
        drama_type = drama.find('span', class_='text-muted').text
        drama_rating = drama.find('span', class_='p-l-xs score').text
        drama_url_relative = drama.find('a')['href']

        # Construct the full URL
        drama_url_full = urljoin('https://mydramalist.com/', drama_url_relative)

        # Check if drama_type contains expected components
        if ' - ' in drama_type and ',' in drama_type:
            # Splitting drama_type and handling variations
            components = list(map(str.strip, drama_type.split(',')))

            # Set default values in case components are missing
            drama_t = drama_year = drama_episodes = ""

            # Assign values if available
            drama_t, rest = components[0].split(' - ', 1)
            drama_year = rest.split()[-1]

            if len(components) > 1:
                drama_episodes = components[1].split()[0]

            # Scrape additional data from the individual drama page
            drama_data = scrape_dramas_page(drama_url_full, drama_title, drama_t, drama_year, drama_rating, drama_episodes)
            results.append(drama_data)

    return results

# Function to scrape data from a given URL
def scrape_dramas_page(drama_url_full, drama_title, drama_t, drama_year, drama_rating, drama_episodes):
    drama_page_html = requests.get(drama_url_full).text
    drama_page_soup = BeautifulSoup(drama_page_html, 'lxml')

    # Find the parent <a> tag with class 'block' which contains the <img> tag
    parent_a_tag = drama_page_soup.find('a', class_='block')

    # Extract the image URL if the parent <a> tag exists and contains the <img> tag with 'src' attribute
    if parent_a_tag and 'src' in parent_a_tag.img.attrs:
        image_url = parent_a_tag.img['src']
    else:
        image_url = None

    # Find all elements with class "show-synopsis"
    drama_overviews = drama_page_soup.find_all(class_="show-synopsis")

    # Iterate over each synopsis_div
    for drama_overview in drama_overviews:
    # Find the span tag within the synopsis_div
        span_tag = drama_overview.find('span')
    
    # Check if the span tag exists
    if span_tag:
     # Extract the text within the span tag
        drama_overview_text = span_tag.text.strip()

        # Decode HTML entities
        drama_overview_text = html.unescape(drama_overview_text)

        # Remove unwanted characters
        drama_overview_text = drama_overview_text.replace('\n', ' ').replace('\r', '').replace('  ', ' ').replace('–', '-')
    
    # Find all elements with class 'text-primary text-ellipsis' within the main cast section
    drama_main_cast_elements = drama_page_soup.find_all('a', class_='text-primary text-ellipsis')   
    
    # Extract text from each main cast element
    drama_main_cast = [cast.text.strip() for cast in drama_main_cast_elements]
    
    # Extract genre and stripe Genre:
    drama_genre_element = drama_page_soup.find('li', class_='list-item p-a-0 show-genres')
    drama_genre = drama_genre_element.text.replace('Genres:', '').strip() if drama_genre_element else ''

    # Extra tag and stripe Tag:
    drama_tag_element = drama_page_soup.find('li', class_='list-item p-a-0 show-tags')
    drama_tag = drama_tag_element.text.replace('Tags:', '').replace('(Vote or add tags)', '').strip() if drama_tag_element else ''

    # Find the first 'box-body light-b' element
    drama_box_elements = drama_page_soup.find_all('div', class_='box-body light-b')

    # Extract information from the first 'box-body light-b' element
    if drama_box_elements:
        drama_box = drama_box_elements[0]

        # Extract information from the first 'ul' element
        drama_ul = drama_box.find('ul', class_='list m-b-0')

        # Extract text from each list item
        drama_items = [item.text.strip() for item in drama_ul.find_all('li')]

        # Create a dictionary to store the extracted information
        drama_data = {}
        for item in drama_items:
            key, value = item.split(':', 1)  # Split each item into key and value
            drama_data[key.strip()] = value.strip()

        # Display data in the terminal
        #print(f"Image URL: {image_url}")  # Print the image URL along with other data
        print(f"Title: {drama_title}")
        print(f"Drama Type: {drama_t}")    
        

        return [drama_title, drama_t, drama_year, drama_rating, drama_episodes, drama_url_full, drama_genre, drama_overview_text, drama_tag,  ', '.join(drama_main_cast),
                            drama_data.get('Country', ''), drama_data.get('Aired', ''), drama_data.get('Aired On', ''),
                             drama_data.get('Original Network', ''), drama_data.get('Duration', ''),
                             drama_data.get('Content Rating', ''), image_url]
    
    # Return an empty list if no data is found
    return []

# Create a CSV file to write the data
csv_file_path = r'E:\Documents\My_Drama_List\dramas_data_test_22May_2024.csv'

def write_to_csv(results):
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['title', 'drama_type', 'year', 'rating', 'episodes', 'url', 'genre', 'overview','tag', 'main_cast',
                             'country', 'aired', 'aired_on', 'original_network', 'duration', 'content_rating', 'image_url'])
        csv_writer.writerows(results)

# Specify the range of pages you want to scrape
urls = [f'https://mydramalist.com/shows/top?page={page_number}' for page_number in range(1, 2)]  # Change the range as needed

# Execute scraping in parallel
with ThreadPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(scrape_dramas, urls))

# Flatten the results list
flat_results = [item for sublist in results for item in sublist]

# Write the data to the CSV file
write_to_csv(flat_results)

# Print a message indicating that the CSV file has been created
print(f"Data exported to {csv_file_path}")
