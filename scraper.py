#!/usr/bin/python3.6
# Ensure we are running as python 3.6 in pythonanywhere

# Import required libraries

import requests  # Makes and returns HTTP requests
from bs4 import BeautifulSoup  # Parses HTML data
from urllib.parse import urljoin  # Allows us to contruct URLs (this is needed for accessing the CSV files)
from io import StringIO  # Allows CSV strings to be treated as if it were a standalone file
import pandas as pd  # Data processing library


# Define a list of given pages
pages = [
    "https://www.ethnicity-facts-figures.service.gov.uk/british-population/demographics/male-and-female-populations/latest",
    "https://www.ethnicity-facts-figures.service.gov.uk/british-population/demographics/working-age-population/latest"
    ]

# Create an empty list variable for storing output data
outputs = []

# Loop over each of our defined pages
for page in pages:
    # Each of our defined pages is assigned the variable 'page'

    # Make HTTP request to get the page content
    page_req = requests.get(page)

    # Parse the response into BeautifulSoup for processing
    soup = BeautifulSoup(page_req.text, 'html.parser')


    # Find page heading
    heading = soup.find('h1', attrs={'class':'heading-large'}).text.strip()


    # Find page metadata
    metadata_element = soup.find('div', attrs={'class':'metadata'})
    metadata_dataframe = pd.DataFrame()
    cleaned_names = []
    for i in metadata_element.find_all('dt'):
        cleaned_names.append(i.text.strip())
    cleaned_values = []
    for i in metadata_element.find_all('dd'):
        cleaned_values.append(i.text.strip())
    metadata_dataframe['Metadata name'] = cleaned_names
    metadata_dataframe['Metadata value'] = cleaned_values


    # Find and access source CSV data
    downloads_elem = soup.find('div', attrs={'class':'downloads'})  # Get the content for the 'Downloads' div
    csv_relative_path = downloads_elem.find('a', attrs={'data-event-action':'Source data'})  # Get the content for the 'Downloads' div
    csv_absolute_path = urljoin(page, csv_relative_path.get('href'))
    csv_req = requests.get(csv_absolute_path)
    downloads_dataframe = pd.read_csv(StringIO(csv_req.text), sep=",")
    output_dataframes.append(downloads_dataframe)

    # Add all output data to the output list as a tuple
    outputs.append((heading, metadata_dataframe, downloads_dataframe))

# Merge all outputs into a single XLS file
writer = pd.ExcelWriter('output.xlsx')
for output in outputs:
    output[1].to_excel(writer, output[0] + ' (Metadata)')
    output[2].to_excel(writer, output[0] + ' (Source data)')
writer.save()
