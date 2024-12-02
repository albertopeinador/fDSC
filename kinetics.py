import streamlit as st
import pandas as pd
import plotly as pt
import plotly.graph_objects as go
import numpy as np
import csv
import plotly.express as px
from io import StringIO
import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex



#   ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––   #

def count_columns(file):    #   Count columns before read to set column names
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

#   ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––   #

def get_names(og_file):     #   Modify column names
    names = list([f'curva {i}' for i in range(count_columns(og_file))])     #   Create default names
    names[0] = 'time'   #   Set first column to time by default
    tableinput = st.toggle('Custom names')  #Ask for name input type: By default: table editor, option for text input
    if  not tableinput:
        editnames = pd.DataFrame([names], columns=names) #  DataFrame so it can be edited with st.data_editor
        newnames = st.data_editor(editnames, use_container_width=True, hide_index = True) #Widget to edit data as table
        edited_names = newnames.iloc[0].astype(str).tolist()    #Turn it back into list
    else:
        entered_names = st.text_area('Enter the column of names for each curve', placeholder = '\n'.join(names[1:]))
        edited_names = entered_names.splitlines()
        if len(names[1:]) != len(edited_names):
            st.write(f'Using default names.\nEnter appropriate list or modify using \'Custom names\' toggle for custom names\nLooking for {len(names[1:])} names, {len(edited_names)} were given')
            
            edited_names = names
        else:
            edited_names = ['time'] + edited_names
    
    return edited_names

#   ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––   #

@st.cache_data
def read_kinetics(og_file, edited_names):   #Actually load data
    return pd.read_csv(og_file, sep=';', decimal=',', skiprows=2, names=edited_names)

#   ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––   #

def kinetics(df, filename):   #Proper processing
    currentfig = go.Figure() #Create current curve being modified

    sub_names = []          #Names of new columns for the subtracted data
    integraciones = []      #List for integral results
    left, right = st.columns([2, 3]) #Main columns for the UI, left for controls and integrals plot and right for plot
    names = df.columns.tolist()     #Get names of the data collumns
    with left:
        curve = st.selectbox('Select curve to edit', names[1:-1]) #Curve selection
    for i in names[1:-1]:
        df[f'{i} subtracted'] = df[i] - df[names[-1]]  #Subtract final (reference) curve from the data
        sub_names.append(f'{i} subtracted')            #Append new column names to list


        if f'max_rangesearch {i}' not in st.session_state:
            st.session_state[f'max_rangesearch {i}'] = [.01, df[names[0]].iloc[-2]]
        '''if i == curve:
            st.slider('Peak search interval',
                    min_value = df[names[0]].iloc[0],
                    max_value = df[names[0]].iloc[-2],
                    value = st.session_state[f'max_rangesearch {i}'],
                    key= f'max_rangesearch {i}',
                    step = 1. / len(df[names[0]]))'''

        max_search_min = df[f'{i} subtracted'].where(
            df[names[0]] >= st.session_state[f'max_rangesearch {i}'][0]
            ).first_valid_index()
        
        max_search_max = df[f'{i} subtracted'].where(
            df[names[0]] >= st.session_state[f'max_rangesearch {i}'][1]
            ).first_valid_index()
        

        #   –––––––––––––– INITIALIZE SESSION_STATES FOR ANNOYING INPUTS –––––––––––––  #

        if f'{i} max' not in st.session_state:
            max_peak_index = df[f'{i} subtracted'].iloc[max_search_min:max_search_max].idxmax()
            st.session_state[f'{i} max'] = [max_peak_index]
        for i in names[1:-1]:
            if f"{i} rlim" not in st.session_state:
                st.session_state[f"{i} rlim"] = 0.038
            if f"{i} rightlim" not in st.session_state:
                st.session_state[f"{i} rightlim"] = 0.038
    if f'has_changed_{curve}' not in st.session_state:
        st.session_state[f'has_changed_{curve}'] = True
    if st.session_state[f"{curve} rlim"] != 0.038:
        st.session_state[f"{curve} rightlim"] = st.session_state[f"{curve} rlim"]
        st.session_state[f'has_changed_{curve}'] = False
    elif st.session_state[f'has_changed_{curve}']:
        st.session_state[f"{curve} rightlim"] = st.session_state[f"{curve} rlim"]

        # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––   #
    
    with left:      #   Number input for right integration limit
        n_inpt, dwld = st.columns(2)
        with n_inpt:
            st.number_input(
                f"Set integration limit of curve = {curve}",
                key=f"{curve} rlim",
                value=st.session_state[f"{curve} rightlim"],
                step = .0001,
                format="%0.4f"
            )

    for i in names[1:-1]:
            #   Initialize limit indexes
        if f't_index {i}' not in st.session_state:  
            st.session_state[f't_index {i}'] = df[names[0]].where(
                df[names[0]] >= st.session_state[f"{i} rightlim"]
                ).first_valid_index()
            #   Update limit indexes
        st.session_state[f't_index {i}'] = df[names[0]].where(
                df[names[0]] >= st.session_state[f"{i} rightlim"]
                ).first_valid_index()
        
        end = min(len(df[names[0]]) - 1, st.session_state[f't_index {i}']) #Making sure not to go over last data point

            #   Initialize baseline value
        if f'baseline {i}' not in st.session_state:
            st.session_state[f'baseline {i}'] = df[f'{i} subtracted'].iloc[end]
            #   Update baseline value
        st.session_state[f'baseline {i}'] = df[f'{i} subtracted'].iloc[end]
        
        #   Left limit detection condition:
        condicion = df[f'{i} subtracted'].iloc[:end] - st.session_state[f'baseline {i}'] < 0
        
        
        #   Initialize left limit index value
        if f'start {i}' not in st.session_state:
            st.session_state[f'start {i}'] = df[f'{i} subtracted'].iloc[:end].where(condicion).last_valid_index()
        #   Update left limit index value        
        st.session_state[f'start {i}'] = df[f'{i} subtracted'].iloc[:end].where(condicion).last_valid_index()
        
        
        #   Initialize subtracted curve value in integration interval
        if f'signal_segment {i}' not in st.session_state:
            st.session_state[f'signal_segment {i}'] = df[f'{i} subtracted'].iloc[st.session_state[f'start {i}']:end+1]
        #   Update subtracted curve value in integration interval
        st.session_state[f'signal_segment {i}'] = df[f'{i} subtracted'].iloc[st.session_state[f'start {i}']:end+1]
        

        #   Initialize values of time in integration interval
        if f'time_segment {i}' not in st.session_state:
            st.session_state[f'time_segment {i}'] = df[names[0]].iloc[st.session_state[f'start {i}']:end+1]
        #   Update values of time in integration interval
        st.session_state[f'time_segment {i}'] = df[names[0]].iloc[st.session_state[f'start {i}']:end+1]
    
        #   Calculate and store integral
        area_max_peak = np.trapz(st.session_state[f'signal_segment {i}'] - st.session_state[f'baseline {i}'], st.session_state[f'time_segment {i}'])
        integraciones.append(area_max_peak)


    #   Add curve (only the integration interval) to the plot. Only for the shading, line left transparent
    currentfig.add_trace(go.Scatter(x = st.session_state[f'time_segment {curve}'],
                                    y = st.session_state[f'signal_segment {curve}'],
                                    showlegend = False,
                                    line = dict(color='rgba(0,0,0,0)')))
    
    #   Add baseline (only the integration interval) to the plot. Only for the shading, line left transparent
    #        fill command in here!
    currentfig.add_trace(go.Scatter(x = st.session_state[f'time_segment {curve}'],
                                    y = [st.session_state[f'baseline {curve}']]*len(st.session_state[f'time_segment {curve}']),
                                    fill = 'tonexty',
                                    fillcolor = '#cccccc',
                                    showlegend = False,
                                    line = dict(color='rgba(0,0,0,0)')))
    
    #   Add full subtracted curve to plot
    currentfig.add_trace(go.Scatter(x = df[names[0]], y = df[f'{curve} subtracted'],
                                    name = f'{curve}\n subtracted',
                                    line = dict(color = '#08a5b9', width = 3)))
    
    #   Format and button to save data as .csv
    integrals_df = pd.DataFrame(list(reversed(integraciones[:])), index = list(reversed([i.replace(',', '.') for i in names[1:-1]])), columns = ['Integral'])
    integrals_df.index.name = 'Curve'
    intes_csv = integrals_df.to_csv()
    with dwld:
        st.download_button('Download Integrals',
                           data = intes_csv,
                           file_name = filename[:-4] + '_integrals.csv',
                           use_container_width = True,
                           )
    
    try:    #   To create integrals plot, error handling for str names instead of floats
        
        #   Colormaps and stuff for pretty graphs
        cmap = plt.get_cmap("Blues")
        colors = np.linspace(0.3, 1, len(names[1:-1]))
        cols = []
        for i in range(len(names[1:-1])):
            color = cmap(colors[i])
            cols.append(str(rgb2hex(color)))

        #   Format the data arrays properly
        inte_x = list([float(i.replace(',', '.')) for i in names[1:-1]])
        inte_y = integraciones[:]

        #   Create integrals plot
        intes = px.scatter(x = inte_x, y = inte_y, log_x = True)
        #   Make colors and marker size for beauty <3
        intes.update_traces(marker = dict(color = cols, size=8))

        with left:
            st.plotly_chart(intes, use_container_width = True) #    Show integrals plot
    except: #   Could not convert names to floats
        with left:
            st.write('Names cant be converted into float to plot')
            st.write('You can still download the calculated integral values')


    #   Change layout of main plot
    currentfig.update_layout(height = 600, xaxis_title='time')
    
    with right:
        st.plotly_chart(currentfig, use_container_width = True) #   Show main plot

        