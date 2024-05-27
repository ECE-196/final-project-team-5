import pdfplumber 
import pandas as pd 
import numpy as np 
import io  
import re
import pprint 
import pathlib


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
                line = self.my_text.readline()  
                if line == '': break    
                if line.strip() in self.ignored_lines or any(re.search(pattern,line.strip()) for pattern in self.dynamic_ignored_lines): continue
                
                if self.block_start[0]=="anon": 
                    if line.strip() in self.my_anon_categories[self.block_start[1]]: self.extract_block(a_line=line)
                elif self.block_start in line: self.extract_block(a_line=line)
                    
            self.my_complete_data_frame=pd.DataFrame(self.df_map)
                
        except Exception as error: 
            print( f"\n The file {a_pdf_file} has failed parsing! \n\n This could be due to incorrect formatting. \n\n Please check the file again. \n\n ERROR MESSAGE: \n\n {error} \n\n" )
            self.valid_db=False
            
    def extract_block(self,a_line):
        temp_category_list=[category for category in self.my_categories]+[anon_category for anon_category in self.my_anon_categories]
  
        while(len(temp_category_list)!=0 ):  
            
            for word in self.my_anon_categories:    
                if a_line.strip() in self.my_anon_categories[word]:  
                    self.df_map[word].append(a_line.strip())  
                    temp_category_list.remove(word)  
                    break
                elif word !=self.block_start[1] and word in temp_category_list: 
                    self.df_map[word].append(np.nan)  
                    temp_category_list.remove(word) 
                    break
                    

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
    
the_PDF_Data=Pdf_Parser(
                        a_pdf_file=f'{pathlib.Path(__file__).resolve().parent}/pdfs/March 23, 2024.pdf', 
                        
                        a_categories=["Date Reported", "Incident/Case#", "Date Occurred", "Time Occurred", "Summary", "Disposition"],   
                        
                        a_anon_categories={ 
                                          
                                         "Crime":[  'Petty Theft ‐ Micro Mobility Device', 
                                                    'Petty Theft - Micro Mobility Device', 
                                                    'Petty Theft of Micro Mobility', 
                                                    'Petty Theft - Micro Mobility Theft',
                                                    'Petty Theft of Micro Mobility Device',
                                                    'Petty Theft ‐ Motor Vehicle Theft',
                                                    'Petty Theft - Micro Mobility Device/ Vandalism'
                                         ],  

                                        "Location":['Matthews Apartments', 
                                                    'Main Gym',
                                                    'Main GYM',
                                                    'Mesa Apartments South',
                                                    'Beagle Hall', 
                                                    'Trolley ‐ Central Campus Station', 
                                                    'Trolley - Central Campus',
                                                    'Trolley ‐ La Jolla Health Station', 
                                                    'Pepper Canyon Hall',
                                                    'Pines Restaurant', 
                                                    'Peterson Hall',
                                                    'Pepper Canyon Apartments',
                                                    'Preuss School',
                                                    'Price Center Plaza',
                                                    'Cala',
                                                    'Cater Hall',
                                                    'Canyon Vista',
                                                    'Center Hall',
                                                    'Center Hall ‐ Outside Bike Rack',
                                                    'Scholars Drive N',
                                                    'Scholars Drive North',
                                                    'Social Sciences Building',
                                                    'Seventh College East #1',
                                                    'Seventh College West #7',
                                                    'Seventh College',
                                                    '9515 Gilman Drive ‐ Bike Rack',
                                                    '9330 Eucalyptus Lane',
                                                    'Gilman Drive',
                                                    'Geisel Library',
                                                    'Ridge Walk Academic',
                                                    'One Miramar Street, Building 4',
                                                    'Innovation Lane',
                                                    'UC San Diego Campus'
                                            ]
                                          
                                          }, 
                        
                        a_ignored_lines=['UCSD POLICE DEPARTMENT', 'CRIME AND FIRE LOG/MEDIA BULLETIN', 'Obstruct-Resist Public Peace Officer'],
                        
                        a_dynamic_ignored_lines=[r'([A-Z][A-Z]+) (\d{1,2}), (\d{4})'], 

                        a_block_start=("anon" , "Crime")
                       )

print(the_PDF_Data.my_complete_data_frame)
