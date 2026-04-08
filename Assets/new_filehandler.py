import re
import bisect as bi
import streamlit as st
#import pandas as pd

def modify_text_file(file_content):
    # Step 1: Read the entire file
    lines = file_content.splitlines()
    
    # Step 2: Remove the last couple of lines
    lines = lines [:1] + lines[2:]
    chip_name = lines[-1].split()[1] + '_'
    if lines[-1][0].isalpha():
        
        lines = lines[:-1]
        
    
    # Step 3: Replace two or more spaces with a tab character
    modified_lines = [line.replace(',', '.') for line in lines]
    modified_lines = [re.sub(r' {2,}', ',', line) for line in modified_lines]
    modified_lines = [re.sub(r'\t{1,}', ',', line) for line in modified_lines]
    #Delte first , in case there is one
    modified_lines = [line.lstrip(',') for line in modified_lines]
    # Step 4: Write the modified lines back to the file
    processed_content = "\n".join(modified_lines)
    return processed_content, chip_name
    



# Modify to take file names and file contents separately
def files_to_dict(files_upload, file_names):
    temps_files = {}
    temps = []
    
    if files_upload is not None:
        # Iterate over the files using both content and name
        for file_content, file_name in zip(files_upload, file_names):
            
            # Use file name to extract temperature info
            match = list(re.finditer(r'(minus|-)?(\d+)\s*(degree|deg|_|ºC)(_ref|r|_Referencia)?(_modified)?', file_name))
            if len(match)>1:
                match = match[1]
            else:
                match=match[0]
            if match:
                if match.group(5):
                    continue
                number_str = match.group(2)
                number = int(number_str)
                if match.group(1):
                    number = -number
                if number not in temps_files:
                    temps_files[number] = [None, None]
                    bi.insort(temps, number)
                # st.write(number)
                # Use file content in the corresponding slots instead of file objects
                if match.group(4) == None:  # ref file
                    temps_files[number][0] = file_content
                
                else:  # regular file
                    temps_files[number][1] = file_content
                
                    

    return temps, temps_files


