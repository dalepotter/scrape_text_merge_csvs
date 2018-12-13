#!/usr/bin/python3.6
# Ensure we are running as python 3.6, given that this code is written to this version

# Import required libraries
import os  # Allows python to interact with the operating system - e.g. check if files exist
from urllib.parse import urljoin  # Allows us to contruct URLs (this is needed for accessing the CSV files)import pandas as pd  # Data processing library

import pandas as pd  # Data processing library
import requests  # Makes and returns HTTP requests
from bs4 import BeautifulSoup  # Parses HTML data
from io import StringIO  # Allows CSV strings to be treated as if it were a standalone file
from openpyxl import load_workbook  # Python Excel library to load an existing xlsx file


# Define a list of given pages to scrape
pages = [
    "https://www.ethnicity-facts-figures.service.gov.uk/british-population/demographics/male-and-female-populations/latest",
    "https://www.ethnicity-facts-figures.service.gov.uk/british-population/demographics/working-age-population/latest",
    "https://www.ethnicity-facts-figures.service.gov.uk/british-population/demographics/socioeconomic-status/latest"
    ]

# Define the file name for the output xlsx file
output_path = 'output.xlsx'

# Create an empty list variable for storing output data
# This will contain a list of lists (with each child list containing a sheet title and dataframe that will be written to Excel)
sheets_to_output = []

# Loop over each of the pages that we want to scrape
for page in pages:
    # Each of our defined pages is assigned the variable 'page'

    # Make HTTP request to get the page content
    page_req = requests.get(page)

    # Parse the response into BeautifulSoup for processing
    soup = BeautifulSoup(page_req.text, 'html.parser')


    # Find page page title (based on the main heading of the page)
    page_title = soup.find('h1', attrs={'class':'heading-large'}).text.strip()
    if len(page_title) > 20:  # Shorten page title if it is too long (.e. greater than 20 characters)
        page_title = page_title[0:20]  # This syntax will reassign the page title to be no greater than the first 20 characters


    # Find page metadata
    metadata_element = soup.find('div', attrs={'class':'metadata'})  # Find a div with class 'metadata'
    metadata_dataframe = pd.DataFrame()  # Create and empty pandas dataframe that represent a sheet for the metadata of the page
    cleaned_names = []  # Empty list to store the metadata names
    for i in metadata_element.find_all('dt'):  # Find and loop over every 'dt' tag within the metadata element
        cleaned_names.append(i.text.strip())  # Add the contents of the 'dt' tag to the list of metadata names
    cleaned_values = []  # Empty list to store the metadata values
    for i in metadata_element.find_all('dd'):  # Find and loop over every 'dd' tag within the metadata element
        cleaned_values.append(i.text.strip())  # Add the contents of the 'dd' tag to the list of metadata names
    metadata_dataframe['Metadata name'] = cleaned_names  # Add list of metadata names to the metadata dataframe
    metadata_dataframe['Metadata value'] = cleaned_values  # Add list of metadata values to the metadata dataframe
    sheets_to_output.append([page_title + ' (Metadata)', metadata_dataframe])  # str + pandas dataframe


    # Get textual page content
    grid_elements = soup.find_all('div', {'class':'grid-row'})  # Look for all div elements with a class of 'grid-row'
                                                                # - This represents a horizontal section of the page that
                                                                # can contain various types of content - e.g a title, a
                                                                # block of content, an image, a graph or an in-page table.
    num = 1  # Set a counter that we will use in the sheet name for each block of content that we find
    for row in grid_elements:  # Iterative over each of the 'grid-row' elements
        if not any([  # Skip over 'grid-row' elements which contain any of the following elements as we don't need to capture these
                row.find('nav'),  # 'nav' elements contain the breadcrumb/navigation menu - this is not needed
                row.find('h1', {'class':'heading-large'}),  # Contains the page title - this is captured elsewhere
                row.find('div', {'class':'metadata'}),  # Contains page metadata - this is captured elsewhere
                row.find('div', {'class':'share'})  # Contains social media share links - this is not needed
            ]):
            dataframe = pd.DataFrame()  # Create an empty pandas dataframe that will represent a sheet of text within this grid element
            dataframe.loc[0,0] = row.text.strip()  # Add the text content of this 'grid-row' element to the first cell of the dataframe
            sheet_name = page_title + ' Text' + str(num)  # Create a name for the sheet (based on the page title and the number of the 'grid-row' element that is being iterated over)
            num += 1  # Increment the counter, so that it is ready for the next 'grid-row' element
            sheets_to_output.append([sheet_name, dataframe])  # Add the sheet name (string) and pandas dataframe tp the list of evental sheets that will be outputted to Excel


    # Find data for each table that exists within the page
    chart_download_elements = soup.findAll('p', {'class':'chart-download'})  # Get all p elements that contain info on downloading table data
    for chart_download_element in chart_download_elements:  # Loop over each table download element
        if 'Download table data (CSV)' not in chart_download_element.text.strip():
            continue  # Filters out chart downloads that do not have a CSV table download option (for example 'chart-download' elements that are PNG image downloads)

        chart_csv_download_element = chart_download_element.find('a', attrs={'data-event-action':'Table as spreadsheet'})  # Get the element that contains a link to download the chart
        chart_title = chart_csv_download_element.get('data-event-label')  # Find the chart title (this is stored as a non-visible attribute
                                                                          # within the element that provides a link to download the CSV data)
        chart_csv_absolute_path = urljoin(page, chart_csv_download_element.get('href'))  # Construct a full URL for the CSV
        chart_csv_req = requests.get(chart_csv_absolute_path)  # Make a request to get the CSV file
        chart_dataframe = pd.read_csv(StringIO(chart_csv_req.text), sep=",")  # Create a pandas dataframe based on the text data within the CSV file
        sheets_to_output.append([page_title + ' - ' + chart_title, chart_dataframe])  # Add the sheet name (string) and pandas dataframe tp the list of evental sheets that will be outputted to Excel

    # Find and access source CSV data
    downloads_elem = soup.find('div', attrs={'class':'downloads'})  # Get the content for div with a class of 'downloads' - this contains the link to the source CSV data
    csv_relative_path = downloads_elem.find('a', attrs={'data-event-action':'Source data'})  #  Get the element that contains a link to download the source CSV file
    csv_absolute_path = urljoin(page, csv_relative_path.get('href'))  # Construct a full URL for the CSV
    csv_req = requests.get(csv_absolute_path)   # Make a request to get the CSV file
    downloads_dataframe = pd.read_csv(StringIO(csv_req.text), sep=",")  # Create a pandas dataframe based on the text data within the CSV file
    sheets_to_output.append([page_title + ' (Source data)', downloads_dataframe])  # Add the sheet name (string) and pandas dataframe tp the list of evental sheets that will be outputted to Excel


# Prepare the single XLS file that will contain the output data
# If a file does not exist at the speficied output filepath, create an empty Excel file - this is needed as the following section of this script assumes a file exists to open
if not os.path.exists(output_path):  # Test if a file exists and the specified output_path
    # This block will only be executed if the specified output_path does NOT exist
    writer = pd.ExcelWriter(output_path)  # Create a pandas object for writing Excel files.
    empty_dataframe = pd.DataFrame()  # Create an empty pandas dataframe - this will represent an empty sheet in the Excel file
    empty_dataframe.to_excel(writer, 'Sheet1', index=False)  # Write the empty dataframe to the file, giving it a generic title of 'Sheet1'
    writer.save()  # Save the empty file.

# Write the output_Excel file containing all of the sheets previously prepared by this script
writer = pd.ExcelWriter(output_path, engine='openpyxl')  # Create a pandas object for writing Excel files.

# After opening the output Excel file, we will first delete all existing sheets from within the Excel file
writer.book = load_workbook(output_path)  # Open the existing Excel file
sheet_names = writer.book.get_sheet_names()  # Get the name of every existing sheet within the Excel file
for sheet in sheet_names:  # Iterate over each sheet within the Excel file
    active_sheet = writer.book.get_sheet_by_name(sheet)  # Load the sheet
    writer.book.remove_sheet(active_sheet)  # Delete the sheet

# Write all of the sheets (previously prepared by this script) to the (currenly empty) output Excel file
for sheet in sheets_to_output:  # Iterate over each of the sheets that we have prepared
    # Each 'sheet' object being iterated over here is a list containing two items:
    #   sheet[0] - a string for the title of the sheet
    #   sheet[1] - a pandas dataframe that represents the contents of the sheet
    sheet_title = sheet[0][0:31]  # Create an explicit variable which is the sheet title trimmed to 31 characters
    sheet[1].to_excel(writer, sheet_title, index=False)  # Write the sheet to the Excel file
writer.save()  # Save the output Excel file when the loop is complete
