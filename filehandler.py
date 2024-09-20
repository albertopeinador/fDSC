import re
import os
import bisect as bi
import pandas as pd

def modify_text_file(file_path, start_cutoff):
    # Step 1: Read the entire file
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Step 2: Remove the last couple of lines
    lines = lines [0:1] + lines[start_cutoff:]

    if lines[-1][0].isalpha():
        lines = lines[:-1]
    
    # Step 3: Replace two or more spaces with a tab character
    modified_lines = [re.sub(r' {2,}', '\t', line) for line in lines]
    modified_lines = [line.replace(',', '.') for line in modified_lines]
    modified_lines = [line.lstrip('\t') for line in modified_lines]
    # Step 4: Write the modified lines back to the file
    with open(file_path.replace('.txt', '_modified.txt'), 'w') as file:
        file.writelines(modified_lines)
    
    #print(f"Modified {file_path}.")


def files_to_dict(main_dir):
    temps_files = {}
    temps = []
    for i in os.listdir(main_dir):
        match = re.search(r'_(minus)?(\d+)\s*(degree|deg)(_ref)?', i)
        if match:
            number_str = match.group(2)
            number = int(number_str)
            if match.group(1):
                number = - number
            if number not in temps_files:
                temps_files[number] = [None, None]
                bi.insort(temps, number)
            if match.group(4):
                temps_files[number][1] = i
            else:
                # Otherwise, place it in the first slot (index 0)
                temps_files[number][0] = i
    return temps, temps_files

def load_files(main_dir, temps, temp_dict):
    big_data = []
    for i in temps:
        abs_path = os.path.join(str(os.getcwd()), main_dir, temp_dict[i][0])
        abs_path_ref = os.path.join(str(os.getcwd()) , main_dir , temp_dict[i][1])
        modify_text_file(abs_path, 75)
        modify_text_file(abs_path_ref, 75)
        df = pd.read_csv(abs_path, sep = '\t', encoding = 'latin1', index_col='Index')
        df_ref = pd.read_csv(abs_path_ref, sep = '\t', encoding = 'latin1', index_col='Index')
        big_data.append((df, df_ref))
    return big_data
