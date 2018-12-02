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

# Create some empty list variables for storing outputs
output_text = []
output_csvs = []

# Loop over each of our defined pages
for page in pages:
    # Each of our defined pages is assigned the variable 'page'

    # Make HTTP request to get the page content
    page_req = requests.get(page)

    # Parse the response into BeautifulSoup for processing
    soup = BeautifulSoup(page_req.text, 'html.parser')

    # Access the text (possibly specific items) - this is the first output1

    # Find and access source CSV data - this is the second output
    downloads_elem = soup.find('div', attrs={'class':'downloads'})  # Get the content for the 'Downloads' div
    csv_relative_path = downloads_elem.find('a', attrs={'data-event-action':'Source data'})  # Get the content for the 'Downloads' div
    csv_absolute_path = urljoin(page, csv_relative_path.get('href'))
    csv_req = requests.get(csv_absolute_path)
    output_csvs.append(csv_req.text)
    dataframe = pd.read_csv(csv_req.text, sep=",")

# Merge all outputs into an XLS
