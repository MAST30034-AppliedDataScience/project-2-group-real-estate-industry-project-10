import requests
import pandas as pd

# Define the URL of the Excel file
url = 'https://www.dffh.vic.gov.au/moving-annual-rents-suburb-march-quarter-2023-excel'

# Send a GET request to download the Excel file
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Save the content as a temporary Excel file
    with open('../data/landing/External_data/historical_data.xlsx', 'wb') as file:
        file.write(response.content)
    print('Excel file downloaded successfully!')

    # Use pandas to read the Excel file
    df = pd.read_excel('../data/landing/External_data/historical_data.xlsx', sheet_name=None)  # sheet_name=None to load all sheets

    # Output the names of all sheets
    print(f"The file contains the following sheets: {list(df.keys())}")

    # Let's assume we want to read the first sheet and print the first few rows
    first_sheet = list(df.keys())[0]  # Get the first sheet's name
    data = df[first_sheet]
    print(data.head())  # Print the first 5 rows of the sheet

else:
    print(f"Failed to download Excel file, HTTP status code: {response.status_code}")