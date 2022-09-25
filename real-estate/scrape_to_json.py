import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time

ads_dataframe = pd.DataFrame(columns=[''])


class BazarakiWebScraper:

    def __init__(self) -> None:
        self.domain = 'https://www.bazaraki.com'
        self.ad_urls = set()
        self.listings = []

    def __get_page(self, page_number):
        if page_number == 1:
            url = f'{self.domain}/real-estate/houses-and-villas-rent/number-of-bedrooms---2/lefkosia-district-nicosia/'
        else:
            url = f'{self.domain}/real-estate/houses-and-villas-rent/number-of-bedrooms---2/lefkosia-district-nicosia/?page={page_number}'

        webpage = requests.get(url)

        return webpage

    def _extract_urls_from_list(self, soup: BeautifulSoup):
        urls = soup.find_all('a')
        for url in urls:
            if str(link := url.attrs['href']).startswith('/adv/'):
                self.ad_urls.add(link)

    def get_ad_urls(self):
        page_number = 1
        webpage = self.__get_page(page_number)
        
        while not webpage.history:
            soup = BeautifulSoup(webpage.content, "html.parser")
            self._extract_urls_from_list(soup)
            
            page_number += 1
            webpage = self.__get_page(page_number)

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

if __name__ == '__main__':
    webscraper = BazarakiWebScraper()
    listing_urls = webscraper.get_ad_urls()

    for url in listing_urls:
        listing = webscraper._get_listing(url)
        page_dictionary_object = webscraper._extract_info_from_listing(listing)
        if page_dictionary_object:
            webscraper.listings.append(page_dictionary_object)

        time.sleep(1)
        
    property_listings = webscraper.listings

    with open('property_listings.json', 'w') as f:
        json.dump(property_listings, f)
