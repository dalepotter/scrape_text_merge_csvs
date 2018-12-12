#!/usr/bin/python3.6
# Ensure we are running as python 3.6 in pythonanywhere

# Import required libraries
import os  # Allows python to interact with the operating system - e.g. check if files exist
import requests  # Makes and returns HTTP requests
from bs4 import BeautifulSoup  # Parses HTML data
from urllib.parse import urljoin  # Allows us to contruct URLs (this is needed for accessing the CSV files)
from io import StringIO  # Allows CSV strings to be treated as if it were a standalone file
from openpyxl import load_workbook  # Python Excel library to load an existing xlsx file
import pandas as pd  # Data processing library


# Define a list of given pages
pages = [
    "https://www.ethnicity-facts-figures.service.gov.uk/british-population/demographics/male-and-female-populations/latest",
    "https://www.ethnicity-facts-figures.service.gov.uk/british-population/demographics/working-age-population/latest",
    "https://www.ethnicity-facts-figures.service.gov.uk/british-population/demographics/socioeconomic-status/latest"
    ]

# Define the file name for the output xlsx file
output_path = 'output.xlsx'

# Create an empty list variable for storing output data
# This will contain a list of lists
sheets_to_output = []

# Loop over each of our defined pages
for page in pages:
    # Each of our defined pages is assigned the variable 'page'

    # Make HTTP request to get the page content
    page_req = requests.get(page)

    # Parse the response into BeautifulSoup for processing
    soup = BeautifulSoup(page_req.text, 'html.parser')


    # Find page page title
    page_title = soup.find('h1', attrs={'class':'heading-large'}).text.strip()
    if len(page_title) > 20: # Shorten page title if it is too long
        page_title = page_title[0:19]


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
    sheets_to_output.append([page_title + ' (Metadata)', metadata_dataframe])  # str + pandas dataframe


    # Get textual page content
    grid_elements = soup.find_all('div', {'class':'grid-row'})
    num = 1
    for row in grid_elements:
        if not any([  # Exclude divs which contain any of the following elements
                row.find('nav'),  # Navigation menu
                row.find('h1', {'class':'heading-large'}),  # Page title
                row.find('div', {'class':'metadata'}),  # Metadata
                row.find('div', {'class':'share'})  # Social media share links
            ]):
            dataframe = pd.DataFrame()
            dataframe.loc[0,0] = row.text.strip()
            dataframe_name = page_title + ' Text' + str(num)
            num += 1
            output = [dataframe_name, dataframe]
            sheets_to_output.append([dataframe_name, dataframe])  # str + pandas dataframe


    # Find data for each table that exists on the page
    chart_download_elements = soup.findAll('p', {'class':'chart-download'})  # Get all p elements that contain info on downloading table data
    chart_dataframes = []  # Make an empty variable for storing in-page table dataframes
    for chart_download_element in chart_download_elements:  # Loop over each table download element
        if 'Download table data (CSV)' not in chart_download_element.text.strip():
            continue  # Filters out chart downloads that do not have a CSV table download option

        chart_title = chart_download_element.find('a', attrs={'data-event-action':'Table as spreadsheet'}).get('data-event-label')
        chart_csv_relative_path = chart_download_element.find('a', attrs={'data-event-action':'Table as spreadsheet'})
        chart_csv_absolute_path = urljoin(page, chart_csv_relative_path.get('href'))
        chart_csv_req = requests.get(chart_csv_absolute_path)
        chart_dataframe = pd.read_csv(StringIO(chart_csv_req.text), sep=",")
        sheets_to_output.append([chart_title, chart_dataframe])

    # Find and access source CSV data
    downloads_elem = soup.find('div', attrs={'class':'downloads'})  # Get the content for the 'Downloads' div
    csv_relative_path = downloads_elem.find('a', attrs={'data-event-action':'Source data'})  # Get the content for the 'Downloads' div
    csv_absolute_path = urljoin(page, csv_relative_path.get('href'))
    csv_req = requests.get(csv_absolute_path)
    downloads_dataframe = pd.read_csv(StringIO(csv_req.text), sep=",")
    sheets_to_output.append([page_title + ' (Source data)', downloads_dataframe])  # str + pandas dataframe


# Merge all outputs into a single XLS file
# Create an empty output.xlsx file if one does not already exist
if not os.path.exists(output_path):
    writer = pd.ExcelWriter(output_path)
    empty_dataframe = pd.DataFrame()
    empty_dataframe.to_excel(writer, 'Sheet1', index=False)
    writer.save()

#  Open the existing output file
writer = pd.ExcelWriter(output_path, engine='openpyxl')

# Delete all existing sheets from within the workbook
writer.book = load_workbook(output_path)  # Open the existing workbook
sheet_names = writer.book.get_sheet_names()  # Get the name of every existing sheet within the workbook
for sheet in sheet_names:  # Iterate over each sheet
    std = writer.book.get_sheet_by_name(sheet)  # Load the sheet
    writer.book.remove_sheet(std)  # Delete the sheet

for sheet in sheets_to_output:
    sheet_title = sheet[0][0:31]  # Strip sheet name to 31 characters
    output_dataframe = sheet[1]
    # TODO: Add sheet name to cell A1 of the sheet)
    #output_dataframe.loc[-1, 1] = sheet[0] # Insert the full sheet title at the top of the dataframe
    #output_dataframe.index = output_dataframe.index + 1  # Shifting the dataframe index
    #output_dataframe = output_dataframe.sort_index()  # Sorting by the index
    output_dataframe.to_excel(writer, sheet_title, index=False)
writer.save()
