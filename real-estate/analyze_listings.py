import pandas as pd
from pathlib import Path
import datetime

DIRECTORY = 'C:/github/bazaraki-webscraper/listings'
file_directory = Path(DIRECTORY).glob('*')


class DataCleaner:

    @staticmethod
    def clean_date_column(input_string: str, file_date):
        """
        Clean a date column from raw input.

        Args:
            input_string (str): The raw date string.
            file_date (str): The date from the filename.

        Returns:
            datetime.datetime: The cleaned date.
        """
        raw_date_string = input_string.split('d: ')[1]

        if 'Today' in raw_date_string:
            file_date_object = datetime.datetime.strptime(file_date, '%m-%d-%Y')
            date_string = file_date_object.strftime('%d.%m.%Y')
        elif 'Yesterday' in raw_date_string:
            file_date_object = datetime.datetime.strptime(file_date, '%m-%d-%Y')
            yesterday_date_object = file_date_object - datetime.timedelta(1)
            date_string = yesterday_date_object.strftime('%d.%m.%Y')
        else:
            date_string = raw_date_string.split(' ')[0]
        
        date_object = datetime.datetime.strptime(date_string, '%d.%m.%Y')
        return date_object

    @staticmethod
    def clean_price_column(price_string: str): 
        """
        Clean a price column from raw input.

        Args:
            price_string (str): The raw price string.

        Returns:
            int or None: The cleaned price as an integer or None if the price cannot be cleaned.
        """
        price, *others = price_string.split()

        if price[0] == u'\N{euro sign}':
            price = price[1:]
        elif not price[0].isdigit():
            return None

        formatted_price = price.replace('.', '')

        return int(formatted_price)
    
    @staticmethod
    def convert_year_to_int(year_string: str):
        """
        Convert year from string to integer

        Args:
            year_string (str): The year string.

        Returns:
            int or -1: The year as an integer or -1 if the year cannot be converted.
        """
        try:
            year_int = int(year_string)
        except ValueError:
            year_int = -1
        
        return year_int
    
    @staticmethod
    def convert_property_area_to_int(area_string: str):
        """
        Convert property area from string to integer

        Args:
            property area_string (str): The property area string.

        Returns:
            int or -1: The property area as an integer or -1 if the property area cannot be converted.
        """
        stringified_area = area_string.split(' ')[0]
        try:
            integer_area = int(stringified_area)
        except ValueError:
            integer_area = -1

        return integer_area
    
    @staticmethod
    def convert_floor_to_int(floor_string: str):
        """
        Convert floor from string to integer

        Args:
            floor_string (str): The property area string.

        Returns:
            int: The property area as an integer.
        """
        if (first_char := floor_string[0]).isdigit():
            return int(first_char)
        else:
            raw_input_list = floor_string.split(' ')
            if raw_input_list[0] == 'Ground':
                return 0


class DataProcessor:

    @staticmethod
    def group_and_aggregate(dataframe: pd.DataFrame):
        """
        Group and aggregate data in the given DataFrame.

        Args:
            dataframe (pd.DataFrame): The DataFrame containing data to be grouped and aggregated.

        Returns:
            None
        """
        grouped_df = dataframe.groupby('Postal code:')
        print('First entry of each group:', grouped_df.first())
        print('2054 group', grouped_df.get_group(2054.0))


class ListingsDF:

    def __init__(self) -> None:
        self.listings_df = None

    def read_files(self, file_directory):
        """
        Read and concatenate data from CSV files in the specified directory.

        Args:
            file_directory (pathlib.Path): The directory containing CSV files.

        Returns:
            None
        """
        for idx, file in enumerate(file_directory):
            file_date = file.name.split('_')[1]
            
            file_df = pd.read_csv(file)
            file_df['Listing Date'] = file_df['listing_date'].apply(DataCleaner.clean_date_column, args=(file_date,))
            if idx == 0:
                self.listings_df = file_df
            else:
                self.listings_df = pd.concat([self.listings_df, file_df], axis=0, ignore_index=True)

    def drop_unnecessary_columns(self):
        """
        Drop unnecessary columns from the DataFrame.

        Args:
            None

        Returns:
            None
        """
        minified_df = self.listings_df.drop(columns=[
            'Reference number:',
            'Type:',
            'Included:',
            'Online viewing:',
            'Air conditioning:',
            'Energy Efficiency:',
            'Registration block:',
            'Registration number:']
            )
        
        self.listings_df = minified_df

    def display_summary(self):
        """
        Display a summary of the DataFrame including its size, head, and data types.

        Args:
            None

        Returns:
            None
        """
        print(f'Dataframe size -> {self.listings_df.shape}')
        print(self.listings_df.head())
        print(self.listings_df.dtypes)

    def groupby_postal_code_construction_year(self):
        group = self.listings_df.groupby(['Postal Code', 'Construction Year', 'Listing Date'])['Price']


    def clean_columns(self):
        """
        Clean and transform columns in the DataFrame.

        Args:
            None

        Returns:
            None
        """
        self.listings_df = self.listings_df.dropna()
        self.listings_df['Price'] = self.listings_df['price'].apply(DataCleaner.clean_price_column)
        self.listings_df['Postal Code'] = self.listings_df['Postal code:'].apply(lambda x: int(x))
        self.listings_df['Construction Year'] = self.listings_df['Construction year:'].apply(DataCleaner.convert_year_to_int)
        self.listings_df['Property Area'] = self.listings_df['Property area:'].apply(DataCleaner.convert_property_area_to_int)
        self.listings_df['Floor'] = self.listings_df['Floor:'].apply(DataCleaner.convert_floor_to_int)
        self.listings_df = self.listings_df.drop(columns=['listing_date', 'Postal code:', 'price', 'Construction year:', 'Property area:', 'Floor:'])
        print(self.listings_df.dtypes)

if __name__ == '__main__':
    listings_dataframe = ListingsDF()
    listings_dataframe.read_files(file_directory)
    listings_dataframe.drop_unnecessary_columns()
    # listings_dataframe.sample_df()
    listings_dataframe.clean_columns()
    listings_dataframe.groupby_postal_code_construction_year()
    # listings_dataframe.aggregate()


