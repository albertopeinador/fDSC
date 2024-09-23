import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import filehandler as tx
import file_loader as ld

fig, ax1= plt.subplots(1, 1, sharex=False, sharey=True)
fig.set_figheight(10, 40)

ctr_panel, graf = st.columns(2)
with ctr_panel:
    folder_name = st.text_input('Folder path', key = 'direc')
    load_cutoff = st.slider('cutoff', min_value=0, max_value=100)
    margin_step = st.slider('margin_step', min_value=0, max_value=100) / 100
    tipo = st.selectbox('Tipo de grafico', ['Tr', 'Ts', 'int'])

if type(folder_name) == type(''):
    temps, file_dict = tx.files_to_dict(folder_name)
    with ctr_panel:
        x = st.selectbox('Ta', temps)
    big_data = ld.load_files(folder_name, temps, file_dict, load_cutoff)
    margin = margin_step * (float(big_data[0][1]['Heat Flow'].max()) - float(big_data[0][1]['Heat Flow'].min()))
    for i in range (1, len(big_data)-1):
        dif = abs(big_data[i][0]['Heat Flow'] - big_data[i-1][0]['Heat Flow']).max()
        big_data[i][0]['Heat Flow'] -= dif + margin
        big_data[i][1]['Heat Flow'] -= dif + margin
        big_data[i][0].plot(x = 'Tr', y = 'Heat Flow', ax = ax1, legend=False, style = '#2ca50b')
        big_data[i][1].plot(x = 'Tr', y = 'Heat Flow', ax = ax1, legend=False, style = '#0886b9', linewidth = 1.6)
        ax1.text(big_data[i][0]['Tr'].iloc[-1], big_data[i][0]['Heat Flow'].iloc[-1], temps[i])
        if len(big_data[i][0]['Heat Flow']) < len(big_data[i][1]['Heat Flow']):
            ax1.fill_between(big_data[i][0]['Tr'], big_data[i][0]['Heat Flow'], big_data[i][1]['Heat Flow'].iloc[:len(big_data[i][0]['Heat Flow'])], color = '#cccccc')
        else:
            ax1.fill_between(big_data[i][1]['Tr'], big_data[i][0]['Heat Flow'].iloc[:len(big_data[i][1]['Heat Flow'])], big_data[i][1]['Heat Flow'], color = '#cccccc')
    ax1.spines['top'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.yaxis.set_ticks([])
    ax1.tick_params(axis='y', which='both', length=0)
    
    
    with graf:
        st.pyplot(fig)

#st.line_chart(data, x = 'Tr', y = 'Heat Flow')
