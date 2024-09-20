import re
import os
import bisect as bi
import pandas as pd

def modify_text_file(file_path):
    # Step 1: Read the entire file
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Step 2: Remove the last couple of lines
    lines = lines [0:1] + lines[2:]

    if lines[-1][0].isalpha():
        lines = lines[:-1]
    
    # Step 3: Replace two or more spaces with a tab character
    modified_lines = [re.sub(r' {2,}', '\t', line) for line in lines]
    modified_lines = [line.replace(',', '.') for line in modified_lines]
    modified_lines = [line.lstrip('\t') for line in modified_lines]
    # Step 4: Write the modified lines back to the file
    with open(file_path.replace('.txt', '_modified.txt'), 'w') as file:
        file.writelines(modified_lines)
    
    print(f"Modified {file_path}.")


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
        modify_text_file(main_dir + temp_dict[i][0])
        modify_text_file(main_dir + temp_dict[i][1])
        df = pd.read_csv(main_dir + temp_dict[i][0], sep = '\t', encoding = 'latin1')
        df_ref = pd.read_csv(main_dir + temp_dict[i][1], sep = '\t', encoding = 'latin1')
        big_data.append((df, df_ref))
    return big_data
