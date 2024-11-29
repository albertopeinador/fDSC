import streamlit as st
import pandas as pd
import plotly as pt
import plotly.graph_objects as go
import csv
from io import StringIO

def count_columns(file):
    """
    Count the number of columns in a CSV file.

    Parameters:
    - file: Uploaded file object from Streamlit's file uploader.

    Returns:
    - int: Number of columns in the file.
    """
    try:
        # Read the first line to determine the number of columns
        first_line = file.readline().decode("utf-8")
        file.seek(0)  # Reset file pointer after reading
        return len(next(csv.reader(StringIO(first_line), delimiter=';')))
    except Exception as e:
        st.error(f"Error while counting columns: {e}")
        return None

def get_names(og_file):
    names = list([f'curva {i}' for i in range(count_columns(og_file))])
    names[0] = 'time'
    tableinput = st.toggle('Custom names')
    if  not tableinput:
        #st.write(names)
        editnames = pd.DataFrame([names], columns=names)
        newnames = st.data_editor(editnames, use_container_width=True, hide_index = True)
        edited_names = newnames.iloc[0].astype(str).tolist()
    else:
        entered_names = st.text_area('Enter the column of names for each curve', placeholder = '\n'.join(names[1:]))
        edited_names = entered_names.splitlines()
        if len(names[1:]) != len(edited_names):
            raise ValueError
        else:
            edited_names = ['time'] + edited_names
    
    return edited_names


@st.cache_data
def read_kinetics(og_file, edited_names):
    return pd.read_csv(og_file, sep=';', decimal=',', skiprows=2, names=edited_names)


def kinetics(df):
    currentfig = go.Figure()

    sub_names = []
    integraciones = []
    left, right = st.columns([2, 3])
    names = df.columns.tolist()
    with left:
        curve = st.selectbox('Select curve to edit', names[1:-1])
    for i in names[1:-1]:
        df[f'{i} substracted'] = df[i] - df[names[-1]]
        sub_names.append(f'{i} substracted')
        
        if f'{i} max' not in st.session_state:
            max_peak_index = df[f'{i} substracted'].iloc[100:500].idxmax()
            st.session_state[f'{i} max'] = [max_peak_index]
        for i in names[1:-1]:
            if f"{i} rlim" not in st.session_state:
                st.session_state[f"{i} rlim"] = 0.
            if f"{i} rightlim" not in st.session_state:
                st.session_state[f"{i} rightlim"] = 0.
    if f'has_changed_{curve}' not in st.session_state:
        st.session_state[f'has_changed_{curve}'] = True
    if st.session_state[f"{curve} rlim"] != 0.:
        st.session_state[f"{curve} rightlim"] = st.session_state[f"{curve} rlim"]
        st.session_state[f'has_changed_{curve}'] = False
    elif st.session_state[f'has_changed_{curve}']:
        st.session_state[f"{curve} rightlim"] = st.session_state[f"{curve} rlim"]
    with left:
        st.number_input(
            f"Set integration limit of curve = {curve}",
            key=f"{curve} rlim",
            value=st.session_state[f"{curve} rightlim"],
        )
    currentfig.add_trace(go.Scatter(x = df[names[0]], y = df[f'{curve} substracted']))
    with right:
        st.plotly_chart(currentfig, use_container_width = True)
        #st.write(f'Actual number: %d' % st.session_state[f"{curve} rightlim"])

        