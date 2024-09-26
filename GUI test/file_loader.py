import filehandler as tx
import os
import pandas as pd

def load_files(main_dir, temps, temp_dict, cutoff):
    big_data = []
    for i in temps:
        abs_path = os.path.join(str(os.getcwd()), main_dir, temp_dict[i][0])
        abs_path_ref = os.path.join(str(os.getcwd()) , main_dir , temp_dict[i][1])
        tx.modify_text_file(abs_path, cutoff)
        tx.modify_text_file(abs_path_ref, cutoff)
        df = pd.read_csv(abs_path.replace('.txt', '_modified.txt'), sep = '\t', encoding = 'unicode_escape', index_col= 'Index')
        df_ref = pd.read_csv(abs_path_ref.replace('.txt', '_modified.txt'), sep = '\t', encoding = 'unicode_escape', index_col= 'Index')
        big_data.append((df, df_ref))
    return big_data