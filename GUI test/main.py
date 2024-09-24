import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import filehandler as tx
import file_loader as ld

#if 'slider_delta' not in st.session_state:
#    st.session_state['slider_delta'] = 0.

def update_slider_value():
    st.session_state[Ta] = st.session_state['slider_delta']


fig, ax1= plt.subplots(1, 1, sharex=False, sharey=True)
fig.set_figheight(10, 40)

ctr_panel, graf = st.columns(2)

with ctr_panel:
    folder_name = st.text_input('Folder path', key = 'direc')
    load_cutoff = st.slider('cutoff', min_value=2, max_value=100)
    margin_step = st.slider('margin_step', min_value=0, max_value=100) / 100
    eje_x = st.selectbox('Eje x', ['Tr', 'Ts', 't'])

try:
    
    temps, file_dict = tx.files_to_dict(folder_name)

    for i in temps:
        if i not in st.session_state:
            st.session_state[i] = 0.

    big_data = ld.load_files(folder_name, temps, file_dict, load_cutoff)
    margin = margin_step * (float(big_data[0][1]['Heat Flow'].max()) - float(big_data[0][1]['Heat Flow'].min()))


    with ctr_panel:
        mod = st.checkbox ('Modify overlap')

    if mod == True:
        plt.cla()
        with ctr_panel:
            Ta = st.selectbox('Ta', temps)
            st.slider('delta', min_value=-1., max_value=1., value = st.session_state[Ta], key='slider_delta', step=0.01, on_change=update_slider_value)
        #st.session_state[Ta] = delta


    for i in range(len(temps)):
        big_data[i][0]['Heat Flow'] += (st.session_state[temps[i]] / 10) * big_data[i][0]['Heat Flow'].max()


    if mod==True:
        big_data[temps.index(Ta)][0].plot(x = eje_x, y = 'Heat Flow', ax = ax1, legend=False, style = '#2ca50b')
        big_data[temps.index(Ta)][1].plot(x = eje_x, y = 'Heat Flow', ax = ax1, legend=False, style = '#0886b9', linewidth = 1.6)
    else:
        for i in range (1, len(big_data)):
            dif = abs(big_data[i][0]['Heat Flow'] - big_data[i-1][0]['Heat Flow']).max()
            big_data[i][0]['Heat Flow'] -= dif + margin
            big_data[i][1]['Heat Flow'] -= dif + margin
        for i in range(len(temps)):    
            big_data[i][0].plot(x = eje_x, y = 'Heat Flow', ax = ax1, legend=False, style = '#2ca50b')
            big_data[i][1].plot(x = eje_x, y = 'Heat Flow', ax = ax1, legend=False, style = '#0886b9', linewidth = 1.6)
            ax1.text(big_data[i][0][eje_x].iloc[-1], big_data[i][0]['Heat Flow'].iloc[-1], temps[i])
            if len(big_data[i][0]['Heat Flow']) < len(big_data[i][1]['Heat Flow']):
                ax1.fill_between(big_data[i][0][eje_x], big_data[i][0]['Heat Flow'], big_data[i][1]['Heat Flow'].iloc[:len(big_data[i][0]['Heat Flow'])], color = '#cccccc')
            else:
                ax1.fill_between(big_data[i][1][eje_x], big_data[i][0]['Heat Flow'].iloc[:len(big_data[i][1]['Heat Flow'])], big_data[i][1]['Heat Flow'], color = '#cccccc')
    ax1.spines['top'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.yaxis.set_ticks([])
    ax1.tick_params(axis='y', which='both', length=0)
    
    with graf:
        st.pyplot(fig)

    print (st.session_state['-80'])


except FileNotFoundError:
    st.title('Enter folder name')
#st.line_chart(data, x = 'Tr', y = 'Heat Flow')
