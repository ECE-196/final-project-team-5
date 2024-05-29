import pdfplumber 
import pandas as pd 
import numpy as np 
import io  
import re
import pprint 
import os 
import glob 
import sqlite3 
import pathlib 
import datetime 
import statistics

class Pdf_Parser: 
    
    def __init__(self, a_pdf_file, a_categories, a_anon_categories, a_ignored_lines, a_dynamic_ignored_lines, a_block_start): 
        self.my_text = io.StringIO(str(self.extract_text_from_pdf(pdf_path=a_pdf_file))) 
        self.my_categories = a_categories 
        self.my_anon_categories=a_anon_categories 
        self.ignored_lines=a_ignored_lines 
        self.dynamic_ignored_lines=a_dynamic_ignored_lines
        self.df_map={**{category:[] for category in self.my_categories},**{anon_category:[] for anon_category in self.my_anon_categories}} 
        self.valid_db=True 
        self.block_start=a_block_start

        try:
            
            while True:  
                # read a line, break if the line is '' [EOF], or continue if its an ignored line.
                line = self.my_text.readline()  
                if line == '': break    
                if line.strip() in self.ignored_lines or any(re.search(pattern,line.strip()) for pattern in self.dynamic_ignored_lines): continue
                
                #if the starting block is an anonymous block, then extract it if it is defined in the anonymous categories. 
                #otherwise, extract the block if it is part of a non-anonymous category
                if self.block_start[0]=="anon": 
                    if line.strip() in self.my_anon_categories[self.block_start[1]]: self.extract_block(a_line=line)
                elif self.block_start[1] in line: self.extract_block(a_line=line)
                    
            self.my_complete_data_frame=pd.DataFrame(self.df_map)
                
        except Exception as error: 
            print( f"\n The file {a_pdf_file} has failed parsing! \n\n This could be due to incorrect formatting. \n\n Please check the file again. \n\n ERROR MESSAGE: \n\n {error} \n\n" )
            self.valid_db=False
            
    def extract_block(self,a_line):
        temp_category_list=[category for category in self.my_categories]+[anon_category for anon_category in self.my_anon_categories]

        #stop the extraction once all categories are accounted for.
        while(len(temp_category_list)!=0 ):  
            
            #if the word is part of an anonymous category, append it. 
            #however if it is NOT YET DEFINED, give it a NaN value
            for word in self.my_anon_categories:    
                if a_line.strip() in self.my_anon_categories[word]:  
                    self.df_map[word].append(a_line.strip())  
                    temp_category_list.remove(word)  
                    break
                elif word !=self.block_start[1] and word in temp_category_list: 
                    self.df_map[word].append(np.nan)  
                    temp_category_list.remove(word) 
                    break
                    
            #if the word in the line is part of the categories list, extract the rest of the line and append it to the dataframe.
            found_word = next((word for word in self.my_categories if word in a_line), None) 
            if found_word is not None:  
                self.df_map[found_word].append(a_line.replace(found_word,' ').strip()) 
                temp_category_list.remove(found_word) 

            a_line = self.my_text.readline()  
            if a_line == '': break    
            if a_line.strip() in self.ignored_lines or any(re.search(pattern,a_line.strip()) for pattern in self.dynamic_ignored_lines): continue

    def extract_text_from_pdf(self,pdf_path):
        text = ''
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + '\n'
        return text
    
class mass_Pdf_Parser: 
    def __init__(self, a_pdf_folder_path, a_ignored_files=[], a_mass_categories=[], a_mass_anon_categories={}, a_mass_ignored_lines=[], a_mass_dynamic_ignored_lines=[], a_mass_block_start=()):  
        self.files_list=self.list_files_in_directory(directory_path=a_pdf_folder_path)

        dfs=[]

        for file in self.files_list:  
            if file not in a_ignored_files: 
                pdf_path=f'{a_pdf_folder_path}\{file}'
                the_PDF_Data=Pdf_Parser( a_pdf_file=pdf_path, a_categories=a_mass_categories, a_anon_categories=a_mass_anon_categories, a_ignored_lines=a_mass_ignored_lines, a_dynamic_ignored_lines=a_mass_dynamic_ignored_lines, a_block_start=a_mass_block_start) 
                if(the_PDF_Data.valid_db):
                    if not the_PDF_Data.my_complete_data_frame.empty: dfs.append(the_PDF_Data.my_complete_data_frame)  
                
        
        self.my_complete_mass_dataframe=pd.concat(dfs, ignore_index=False) 

    def list_files_in_directory(self,directory_path):
        search_pattern = os.path.join(directory_path, '*')
        
        files = [os.path.basename(file) for file in glob.glob(search_pattern) if os.path.isfile(file)]
        
        return files  

aMassParser=mass_Pdf_Parser( 
            a_pdf_folder_path=f'{pathlib.Path(__file__).resolve().parent}/pdfs', 

            a_ignored_files=['April 24, 2024.pdf'],

            a_mass_categories=["Date Reported", "Incident/Case#", "Date Occurred", "Time Occurred", "Summary", "Disposition"],   
            
            a_mass_anon_categories={ 
                            
                                "Crime":['Petty Theft ‐ Micro Mobility Device', 
                                         'Petty Theft - Micro Mobility Device', 
                                         'Petty Theft of Micro Mobility', 
                                         'Petty Theft - Micro Mobility Theft',
                                         'Petty Theft of Micro Mobility Device',
                                         'Petty Theft ‐ Motor Vehicle Theft',
                                         'Petty Theft - Micro Mobility Device/ Vandalism', 
                                         'Petty Theft'
                                         ],  

                                "Location":['Matthews Apartments', 
                                            'Main Gym', 
                                            'Main GYM',
                                            'Mesa Apartments South',

                                            'Beagle Hall', 

                                            'Trolley ‐ Central Campus Station',
                                            'Trolley - Central Campus Station' 
                                            'Trolley - Central Campus',
                                            'Trolley ‐ La Jolla Health Station', 
                                            'Torrey Pines Center ‐ South',
                                            'Thurgood Marshall',
                                            

                                            'Pepper Canyon Hall',
                                            'Pines Restaurant', 
                                            'Peterson Hall',
                                            'Pepper Canyon Apartments',
                                            'Preuss School',
                                            'Price Center Plaza',
                                            'Piedra Apartments', 
                                            'Price Center West ‐ Target',

                                            'Cala',
                                            'Cater Hall',
                                            'Canyon Vista',
                                            'Center Hall',
                                            'Center Hall ‐ Outside Bike Rack',
                                            'Coast Graduate Housing', 
                                            'Computer Science & Engineering Building',

                                            'Scholars Drive N',
                                            'Scholars Drive North',
                                            'Social Sciences Building',
                                            'Seventh College East #1',
                                            'Seventh College West #7',
                                            'Seventh College',

                                            '9515 Gilman Drive ‐ Bike Rack',
                                            '9330 Eucalyptus Lane',
                                            '1 Miramar Street Complex, Between Building #1 & #2',

                                            'Gilman Drive',
                                            'Geisel Library',

                                            'Ridge Walk Academic',
                                            'Ridge walk Academic Complex',
                                            'Rita Atkinson',
                                            'RIMAC',

                                            'One Miramar Street, Building 4',
                                            'Otterson Hall',
                                            'One Miramar Street, Building 1',

                                            'Innovation Lane', 
                                            'Design & Innovation Building',

                                            'UC San Diego Campus',
                                            'UCSD Medical Center ‐ La Jolla',

                                            'Jacobs Medical Center',
                                            'Neighborhood ‐ Coast Apartments',

                                            'Erc Footbridge',  
                                            'Equality Lane/ Canyon Vista',
                                            
                                            'Halicioglu Data Science Institute',

                                            'Latin America Hall & North America Hall',
                                            'Library Walk',
                                            
                                            'Warren Lecture Hall',

                                            'Parking Lot P701',

                                            'York Hall',
                                            'Franklin Antonio Hall',
                                           
                                            'Argo Hall',
                                            'Applied Physics and Mathematics',
                                            'Atkinson Hall'
                                            
                                            ] 
                            
                            }, 
            
            a_mass_ignored_lines=['UCSD POLICE DEPARTMENT', 'CRIME AND FIRE LOG/MEDIA BULLETIN', 'Obstruct-Resist Public Peace Officer'],
            
            a_mass_dynamic_ignored_lines=[r'([A-Z][A-Z]+) (\d{1,2}), (\d{4})'], 

            a_mass_block_start=("anon", "Crime")

)  

def time_parser(time_string, truncate=False): 
    ''' 
    use .split() by "-" to split up the timestring 
    
    iterate through the timestring and convert to military time

    take the average regardless of how many entries 

    once thats done truncate the time and only leave the hour  

    then convert back to normal time and return the value
    '''  
    delimiter= "-" if "-" in time_string else "‐"
    time_string.replace(" ","")
    times=time_string.split(delimiter)  

    print(times)
    minutes=[]
    
    for time in times:  
        try: parsed_time = datetime.datetime.strptime(time.replace(" ",""), '%I:%M%p')
        except: return np.nan
        minutes.append(parsed_time.hour * 60 + parsed_time.minute) 
    
    average_minutes=int(statistics.mean(minutes)) 

    hours, minutes = divmod(average_minutes, 60)

    time_obj = datetime.datetime(1, 1, 1, hours, minutes) if truncate == False else datetime.datetime(1, 1, 1, hours, 0) 

    return time_obj.strftime('%I:%M%p')     



master_df_sorted = aMassParser.my_complete_mass_dataframe.sort_values(by='Date Reported') 
filtered_df = master_df_sorted[
            (master_df_sorted['Crime'] == 'Petty Theft ‐ Micro Mobility Device') |
            (master_df_sorted['Crime'] == 'Petty Theft - Micro Mobility Device') |
            (master_df_sorted['Crime'] == 'Petty Theft of Micro Mobility')| 
            (master_df_sorted['Crime'] == 'Petty Theft - Micro Mobility Theft')| 
            (master_df_sorted['Crime'] == 'Petty Theft of Micro Mobility Device')| 
            (master_df_sorted['Crime'] == 'Petty Theft ‐ Motor Vehicle Theft')| 
            (master_df_sorted['Crime'] == 'Petty Theft - Micro Mobility Device/ Vandalism')| 
            ((master_df_sorted['Crime'] == 'Petty Theft') & master_df_sorted['Summary'].str.contains('bicycle|scooter|bike', case=False, na=False))
            ]
  
filtered_df.loc[:, 'Time Occurred'] = filtered_df['Time Occurred'].apply(time_parser, args=(True,))



conn = sqlite3.connect(f'{pathlib.Path(__file__).resolve().parent}/police_data.db')

# Write the DataFrame to the SQLite3 database
filtered_df.to_sql('users', conn, if_exists='replace', index=False)

# Close the connection
conn.close()

#print(filtered_df['Location'].value_counts())  
#print(filtered_df['Time Occurred'].value_counts())
#print(filtered_df)
