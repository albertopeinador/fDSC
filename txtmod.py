import re
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

# Example usage
file_path = r'C:\Users\albpe\OneDrive - Universidade da Coruña\Escritorio\fDSC\90816 (Bulk 80kDa)\Annealing30min2kto260\Segment138_180deg.txt'
num_lines_to_delete = 2  # Number of lines you want to delete from the end
modify_text_file(file_path)