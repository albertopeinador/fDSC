import re
import os

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


def get_files_dict(main_dir):
    temps = {}
    '''    for i in os.listdir(main_dir):
        match = re.search(r'_(minus )?(\d+)\s*degree(_ref)?', i)
        print (match)
        if match:
            number_str = match.group(2)
            number = int(number_str)
            if match.group(1):
                number = -number
            if number not in temps:
                temps[number] = [None, None]
            if match.group(3):
                temps[number][1] = i
            else:
                # Otherwise, place it in the first slot (index 0)
                temps[number][0] = i
    '''
    for i in os.listdir(main_dir):
        match = re.search(r'_(minus )?(\d+)\s*degree(_ref)?', i)
        if match:
            number_str = match.group(2)
            number = int(number_str)
            if match.group(1):
                number = -number
            if number not in temps:
                temps[number] = [None, None]
            if match.group(3):
                temps[number][1] = i
            else:
                # Otherwise, place it in the first slot (index 0)
                temps[number][0] = i
    return temps


#print(os.listdir('/Users/albertopeinador/Desktop/fDSC/90816 (Bulk 80kDa)/Annealing30min2kto260'))
print (get_files_dict('/Users/albertopeinador/Desktop/fDSC/90816 (Bulk 80kDa)/Annealing30min2kto260'))