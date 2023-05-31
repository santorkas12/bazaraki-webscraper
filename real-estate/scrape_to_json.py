import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
from json_to_df import CSVWriter
import sys

ads_dataframe = pd.DataFrame(columns=[''])


class BazarakiWebScraper:

    def __init__(self) -> None:
        self.domain = 'https://www.bazaraki.com'
        self.ad_urls = set()
        self.listings = []

    def _setup_url(self, **request_info):
        url = f'{self.domain}/{request_info.get("rent_or_buy")}/{request_info.get("type_of_property")}/{request_info.get("no_bedrooms")}/{request_info.get("district")}/'
        return url

    def __get_page(self, url, page_number):
        print(f'Getting page {page_number}')
        if page_number > 1:
            url = f'{url}?page={page_number}'

        webpage = requests.get(url)

        return webpage

    def _extract_urls_from_list(self, soup: BeautifulSoup):
        urls = soup.find_all('a')
        for url in urls:
            if str(link := url.attrs['href']).startswith('/adv/'):
                self.ad_urls.add(link)

    def get_ad_urls(self, url):
        page_number = 1
        webpage = self.__get_page(url, page_number)
        
        while not webpage.history:
            soup = BeautifulSoup(webpage.content, "html.parser")
            self._extract_urls_from_list(soup)
            
            page_number += 1
            webpage = self.__get_page(url, page_number)

        return self.ad_urls

    def _get_listing(self, listing_url):
        domain = 'https://www.bazaraki.com'
        request_url = f'{domain}{listing_url}'

        listing = requests.get(request_url)
        return listing

    def _extract_info_from_listing(self, listing):
        listing_soup = BeautifulSoup(listing.content, "html.parser")
        listing_dictionary = {}

        try:
            id = listing_soup.find('span', attrs={'class': 'number-announcement'}).contents[1].text
        except AttributeError:
            id = 'Not found'

        try:
            title = listing_soup.find('h1', attrs={'id': 'ad-title'}).string.strip()
        except AttributeError:
            title = 'Not found'
        try:
            listing_date = listing_soup.find('span', attrs={'class': 'date-meta'}).string
        except AttributeError:
            listing_date = 'Not found'

        try:
            address = listing_soup.find('span', attrs={'itemprop': 'address'}).string
        except AttributeError:
            address = 'Not found'

        try:
            price = listing_soup.find('div', attrs={'class': 'announcement-price__cost'}).text.strip()
        except AttributeError:
            price = 'Not found'

        try:
            property_chars_html = listing_soup.find('ul', attrs={'class': 'chars-column'}).findChildren('li', attrs={'class': ''})
        except AttributeError:
            property_chars_html = 'Not found'        

        property_characteristics = {}

        if not isinstance(property_chars_html, str):
            for char in property_chars_html:
                char_keys = char.findChildren('span', attrs={'class': 'key-chars'})[0].text
                char_values = char.findChildren('a', attrs={'class': 'value-chars'})
                char_values.extend(char.findChildren('span', attrs={'class': 'value-chars'}))
                char_values = char_values[0].text
                
                property_characteristics[char_keys] = char_values.strip()

            listing_dictionary = {
                'id': id,
                'title': title,
                'listing_date': listing_date,
                'url': listing.url,
                'address': address,
                'price': price,
                'property_characteristics': property_characteristics
            }

            return listing_dictionary

    def create_listing_df(self, listing_urls):
        pass


    def collect_request_params(self):
        if __name__ == '__main__':
            rent_or_buy = input("Are you looking to rent or buy a property? (rent|buy)")
            type_of_property = input("What type of property are you looking for? (apartments-flats|houses|plots-of-land)")
            if type_of_property in {'apartments-flats', 'houses'}:
                no_bedrooms = input('How many bedrooms? (1|2|3|4|5)')
                no_bedrooms = f'number-of-bedrooms---{no_bedrooms}'
        else:
            rent_or_buy = sys.argv[1]
            type_of_property = sys.argv[2]
            if type_of_property in {'apartments-flats', 'houses'}:
                no_bedrooms = sys.argv[3]
                no_bedrooms = f'number-of-bedrooms---{no_bedrooms}'

        if rent_or_buy == 'rent':
            rent_or_buy = 'real-estate-to-rent'
        else:
            rent_or_buy = 'real-estate-for-sale'

        district = 'lefkosia-district-nicosia'

        request_info = {
            'rent_or_buy': rent_or_buy,
            'type_of_property': type_of_property,
            'district': district,
            'no_bedrooms': locals().get('no_bedrooms')
            }
        
        return request_info


if __name__ == '__main__':
    webscraper = BazarakiWebScraper()
    request_params = webscraper.collect_request_params()
    print(f'Running script with params {json.dumps(request_params)}')
    url = webscraper._setup_url(**request_params)
    listing_urls = webscraper.get_ad_urls(url)

    for index, url in enumerate(listing_urls):
        print(f'Processing url {index+1} of {len(listing_urls)}')
        listing = webscraper._get_listing(url)
        page_dictionary_object = webscraper._extract_info_from_listing(listing)
        if page_dictionary_object:
            webscraper.listings.append(page_dictionary_object)

        time.sleep(1)
        
    property_listings = webscraper.listings

    with open('property_listings.json', 'w') as f:
        json.dump(property_listings, f)

    csv_writer = CSVWriter()
    csv_writer.write_to_csv()
