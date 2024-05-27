import pdfplumber
import pandas as pd

# Define the path to your PDF file
pdf_path = 'May 18, 2024.pdf'

# Initialize an empty list to store the extracted data
data = []

# Open the PDF file
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            lines = text.split('\n')
            record = {}
            for line in lines:
                if line.startswith('Date Reported'):
                    # Append the previous record if it's complete
                    if record:
                        data.append(record)
                    # Create a new record
                    record = {
                        'Date Reported': line.split('Date Reported ')[1].strip(),
                        'Incident/Case#': '',
                        'Date Occurred': '',
                        'Time Occurred': '',
                        'Crime': '',
                        'Location': '',
                        'Summary': '',
                        'Disposition': ''
                    }
                elif line.startswith('Incident/Case#'):
                    record['Incident/Case#'] = line.split('Incident/Case# ')[1].strip()
                elif line.startswith('Date Occurred'):
                    record['Date Occurred'] = line.split('Date Occurred ')[1].strip()
                elif line.startswith('Time Occurred'):
                    record['Time Occurred'] = line.split('Time Occurred ')[1].strip()
                elif line.startswith('Crime:'):
                    record['Crime'] = line.split('Crime: ')[1].strip()
                elif line.startswith('Location:'):
                    record['Location'] = line.split('Location: ')[1].strip()
                elif line.startswith('Summary:'):
                    record['Summary'] = line.split('Summary: ')[1].strip()
                elif line.startswith('Disposition:'):
                    record['Disposition'] = line.split('Disposition: ')[1].strip()
                    # Append the complete record to the data list
                    data.append(record)
            # Append the last record if the file ends without 'Disposition:'
            if record:
                data.append(record)

# Convert the list of dictionaries into a DataFrame
df = pd.DataFrame(data)

# Print the DataFrame
print(df)

# Optionally, save the DataFrame to a CSV file
df.to_csv('extracted_data.csv', index=False)