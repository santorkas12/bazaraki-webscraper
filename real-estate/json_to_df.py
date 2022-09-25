import json
import pandas as pd

pd.set_option('display.max_columns', None)

if __name__ == '__main__':
    with open('property_listings.json', 'r') as f:
        property_listings = json.load(f)


    sample_dataframe = pd.DataFrame(property_listings)

    list_of_property_chars = sample_dataframe['property_characteristics'].to_list()
    list_of_ids = sample_dataframe['id'].to_list()

    property_characteristics = pd.DataFrame(list_of_property_chars)

    listings_dataframe = pd.concat([sample_dataframe, property_characteristics], axis=1)
    listings_dataframe.drop('property_characteristics', axis=1, inplace=True)
    listings_dataframe.to_csv('listings.csv')