import requests
from bs4 import BeautifulSoup
import os 
import pathlib

# Step 1: Fetch the HTML content of the webpage

url = 'https://www.police.ucsd.edu/docs/reports/CallsandArrests/Calls_and_Arrests.asp'  # Replace with the actual URL
base_url = 'https://www.police.ucsd.edu/docs/reports/CallsandArrests/'  # Replace with the actual URL

response = requests.get(url)
html_content = response.content

# Step 2: Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Step 3: Locate the <select> tag with the name "ReportLookUp"
select_tag = soup.find('select', {'name': 'ReportLookUp'})

# Ensure the <select> tag was found
if not select_tag:
    raise ValueError("No select tag found with the name 'ReportLookUp'")

# Step 4: Extract URLs from the <option> tags within the <select> tag
options = select_tag.find_all('option')

# Directory to save the PDFs
save_dir = f'{pathlib.Path(__file__).resolve().parent}/pdfs'
os.makedirs(save_dir, exist_ok=True)

# Step 5: Loop through the options and download each PDF
for option in options:
    pdf_url = base_url+'/'+option['value']  # Assumes the URL is in the value attribute  
    # Create the filename from the URL 
    filename = os.path.join(save_dir, pdf_url.split('/')[-1])

    if pdf_url.endswith('.pdf') and not os.path.exists(filename):
        # Download the PDF
        pdf_response = requests.get(pdf_url)
        with open(filename, 'wb') as f:
            f.write(pdf_response.content)

        print(f'Downloaded: {filename}')

print('All PDFs downloaded.')