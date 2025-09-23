import hashlib
import re
import pandas as pd
from io import StringIO
import Assets.new_filehandler as fh
import streamlit as st

# Function to compute the hash of file content
def compute_file_hash(file):
    file_content = file.read()
    file.seek(0)  # Reset the file pointer
    return hashlib.md5(file_content).hexdigest(), file_content

@st.cache_data
def load_files(file_contents, file_names, load_lims, eje_x):


    big_data = {}
    
    # Pass both file contents and file names
    temps, file_dict = fh.files_to_dict(file_contents, file_names)

    for t in temps:
        file_0_content = file_dict[t][0]
        file_1_content = file_dict[t][1]

        if file_0_content is not None and file_1_content is not None:
            mod = fh.modify_text_file(file_0_content.decode('latin1'))
            mod_ref = fh.modify_text_file(file_1_content.decode('latin1'))
            df = pd.read_csv(StringIO(mod), sep=',', encoding='latin1', skipinitialspace=True)
            df = df.apply(pd.to_numeric, errors='coerce')
            df = df[(df[eje_x] >= load_lims[0]) & (df[eje_x] <= load_lims[1])]
            dfref = pd.read_csv(StringIO(mod_ref), sep=',', encoding='latin1', skipinitialspace=True)
            dfref = dfref.apply(pd.to_numeric, errors='coerce')
            dfref = dfref[(dfref[eje_x] >= load_lims[0]) & (dfref[eje_x] <= load_lims[1])]
            big_data[t] = (df,dfref)
        elif file_0_content is None:
            mod_ref = fh.modify_text_file(file_1_content.decode('latin1'))
            df = pd.read_csv(StringIO(mod_ref), sep=',', encoding='latin1', skipinitialspace=True)
            df = df.apply(pd.to_numeric, errors='coerce')
            df = df[(df[eje_x] >= load_lims[0]) & (df[eje_x] <= load_lims[1])]
            big_data[t] = (None, df)
        elif file_1_content is None:
            mod = fh.modify_text_file(file_0_content.decode('latin1'))
            df = pd.read_csv(StringIO(mod), sep=',', encoding='latin1', skipinitialspace=True)
            df = df.apply(pd.to_numeric, errors='coerce')
            df = df[(df[eje_x] >= load_lims[0]) & (df[eje_x] <= load_lims[1])]
            big_data[t] = (df, None)

    return temps, big_data
