# Import required libraries
import requests  # Makes and returns HTTP requests

# Define a list of pages
pages = [
    "https://www.ethnicity-facts-figures.service.gov.uk/british-population/demographics/male-and-female-populations/latest",
    "https://www.ethnicity-facts-figures.service.gov.uk/british-population/demographics/working-age-population/latest"
    ]

# For a list of given webpages
for page in pages:
    # Each of our defined pages is assigned the variable 'page'

    # Make HTTP request to get the page content
    req = requests.get(page)

    # Access the text (possibly specific items) - this is 'output1'

    # Access CSV data (own file) - this is 'output2'


# Merge all outputs into an XLS