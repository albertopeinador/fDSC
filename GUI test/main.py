import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import filehandler as tx
import file_loader as ld
import find_and_int as fai
import numpy as np

st.set_page_config(layout="wide")

st.markdown("""
<style>
.big-font {
    font-size:50px !important;
    text-align:center !important;
}
</style>
""", unsafe_allow_html=True)
#if 'slider_delta' not in st.session_state:
#    st.session_state['slider_delta'] = 0.

def update_slider_value():
    st.session_state[Ta] = st.session_state['slider_delta']

def update_slider_value_left():
    st.session_state['regs_'+str(Ta)][0] = st.session_state['slider_left']

def update_slider_value_right():
    st.session_state['regs_'+str(Ta)][1] = st.session_state['slider_right']

def update_color():
    st.session_state['color'] = st.session_state['main_color']

def update_ref():
    st.session_state['ref'] = st.session_state['ref_color']

def update_shade():
    st.session_state['shade'] = st.session_state['shade_color']

if 'color' not in st.session_state:
    st.session_state['color'] = '#2ca50b'
if 'ref' not in st.session_state:
    st.session_state['ref'] = '#0886b9'
if 'shade' not in st.session_state:
    st.session_state['shade'] = '#cccccc'

fig, ax1= plt.subplots(1, 1, sharex=False, sharey=True)
fig.set_figheight(9)
fig2, ax2= plt.subplots(1, 1, sharex=False, sharey=True)
fig2.set_figheight(5)

ctr_panel, graf, inte = st.columns([.2, .4, .4])

int_dif_th = 0.

with ctr_panel:
    folder_name = st.text_input('Folder name', key = 'direc')
    load_cutoff = st.slider('cutoff', min_value=2, max_value=100, value = 75)
    margin_step = st.slider('margin_step', min_value=0, max_value=100, value = 10) / 100
    eje_x = st.selectbox('x axis', ['Tr', 'Ts', 't'])
    #int_dif_th = st.slider('integral threshold', min_value=0, max_value=100) / 1000

try:
    
    temps, file_dict = tx.files_to_dict(folder_name)

    for i in temps:
        if i not in st.session_state:
            st.session_state[i] = 0.

    big_data = ld.load_files(folder_name, temps, file_dict, load_cutoff)
    
    margin = margin_step * (float(big_data[0][1]['Heat Flow'].max()) - float(big_data[0][1]['Heat Flow'].min()))

    int_regs = {}
    ints = []
    lims = {}

    with ctr_panel:
        mod = st.checkbox ('Modify overlap')

    if mod:
        plt.cla()
        with ctr_panel:
            Ta = st.selectbox('Ta', temps)
            st.slider('delta', min_value=-1., max_value=1., value = st.session_state[Ta], key='slider_delta', step=0.01, on_change=update_slider_value)
        #st.session_state[Ta] = delta


    for i in range(len(temps)):
        big_data[i][0]['Heat Flow'] += (st.session_state[temps[i]] / 10) * big_data[i][0]['Heat Flow'].max()
        regs, left, right = fai.find_int_region(big_data[i], int_dif_th*(big_data[i][0]['Heat Flow'] - big_data[i][1]['Heat Flow']).max(), 'Heat Flow')
        lims[temps[i]] = (left, right)
        int_regs[temps[i]] = regs

        #ints.append(fai.integ(int_regs[temps[i]], 'Heat Flow', 't'))
        #ax2.plot(temps[i], ints[i], 'ks')
        regs_label = 'regs_' + str(temps[i])
        if regs_label not in st.session_state:
            st.session_state[regs_label] = [big_data[i][0][eje_x].iloc[left],big_data[i][0][eje_x].iloc[right]]
        indices = big_data[i][0][eje_x][(big_data[i][0][eje_x] >= st.session_state[regs_label][0]) & (big_data[i][0][eje_x] <= st.session_state[regs_label][1])].index
        ints.append(np.trapz(big_data[i][0]['Heat Flow'][indices.min():indices.max()]-big_data[i][1]['Heat Flow'][indices.min():indices.max()], big_data[i][0]['t'][indices.min():indices.max()]))
    ax2.plot(temps, ints, 'ks')

    if mod:
        dif = big_data[temps.index(Ta)][0]['Heat Flow'] - big_data[temps.index(Ta)][1]['Heat Flow']
        big_data[temps.index(Ta)][0].plot(x = eje_x, y = 'Heat Flow', ax = ax1, legend=False, style = st.session_state['color'])
        big_data[temps.index(Ta)][1].plot(x = eje_x, y = 'Heat Flow', ax = ax1, legend=False, style = st.session_state['ref'], linewidth = 1.6)
        ax1.axvline(x=st.session_state['regs_'+str(Ta)][0], color='r', linestyle='--') #big_data[temps.index(Ta)][0][eje_x][lims[Ta][0]]
        ax1.axvline(x=st.session_state['regs_'+str(Ta)][1], color='r', linestyle='--')
        if len(big_data[temps.index(Ta)][0][eje_x]) == len(dif):
            ax1.plot(big_data[temps.index(Ta)][0][eje_x], dif, 'r') #[lims[Ta][0]:lims[Ta][1]+2]
        else:
            ax1.plot(big_data[temps.index(Ta)][1][eje_x], dif, 'r') #[lims[Ta][0]:lims[Ta][1]+2]
        if len(big_data[temps.index(Ta)][0]['Heat Flow']) < len(big_data[temps.index(Ta)][1]['Heat Flow']):
            ax1.fill_between(big_data[temps.index(Ta)][0][eje_x], big_data[temps.index(Ta)][0]['Heat Flow'], big_data[temps.index(Ta)][1]['Heat Flow'].iloc[:len(big_data[temps.index(Ta)][0]['Heat Flow'])], color = st.session_state['shade'])
        else:
            ax1.fill_between(big_data[temps.index(Ta)][1][eje_x], big_data[temps.index(Ta)][0]['Heat Flow'].iloc[:len(big_data[temps.index(Ta)][1]['Heat Flow'])], big_data[temps.index(Ta)][1]['Heat Flow'], color = st.session_state['shade'])
    with inte:
        st.pyplot(fig2)
    if mod:
        with inte:
            if eje_x == 't':
                st.slider('left integration limit', min_value = big_data[temps.index(Ta)][0][eje_x].min(), max_value = float(st.session_state['regs_'+str(Ta)][1]), value = float(st.session_state['regs_'+str(Ta)][0]), key = 'slider_left', on_change=update_slider_value_left, step = 0.001)
            else:    
                st.slider('left integration limit', min_value = big_data[temps.index(Ta)][0][eje_x].min(), max_value = float(st.session_state['regs_'+str(Ta)][1]), value = float(st.session_state['regs_'+str(Ta)][0]), key = 'slider_left', on_change=update_slider_value_left, step = 0.1)
            if eje_x == 't':
                st.slider('right integration limit', min_value = float(st.session_state['regs_'+str(Ta)][0]), max_value = big_data[temps.index(Ta)][0][eje_x].max(), value = float(st.session_state['regs_'+str(Ta)][1]), key = 'slider_right', on_change=update_slider_value_right, step = 0.001)
            else:    
                st.slider('right integration limit', min_value = float(st.session_state['regs_'+str(Ta)][0]), max_value = big_data[temps.index(Ta)][0][eje_x].max(), value = float(st.session_state['regs_'+str(Ta)][1]), key = 'slider_right', on_change=update_slider_value_right, step = 0.1)
            col, ref, shading = st.columns(3)
            with col:
                st.color_picker('Curve color', value = st.session_state['color'], key = 'main_color', on_change = update_color)
            with ref:
                st.color_picker('Reference color', value = st.session_state['ref'], key = 'ref_color', on_change = update_ref)
            with shading:
                st.color_picker('Shading color', value = st.session_state['shade'], key = 'shade_color', on_change = update_shade)
    if mod==False:
        for i in range (1, len(big_data)):
            dif = abs(big_data[i][0]['Heat Flow'] - big_data[i-1][0]['Heat Flow']).max()
            big_data[i][0]['Heat Flow'] -= dif + margin
            big_data[i][1]['Heat Flow'] -= dif + margin
        for i in range(len(temps)):    
            big_data[i][0].plot(x = eje_x, y = 'Heat Flow', ax = ax1, legend=False, style = st.session_state['color'])
            big_data[i][1].plot(x = eje_x, y = 'Heat Flow', ax = ax1, legend=False, style = st.session_state['ref'], linewidth = 1.6)
            ax1.text(big_data[i][0][eje_x].iloc[-1], big_data[i][0]['Heat Flow'].iloc[-1], temps[i])
            if len(big_data[i][0]['Heat Flow']) < len(big_data[i][1]['Heat Flow']):
                ax1.fill_between(big_data[i][0][eje_x], big_data[i][0]['Heat Flow'], big_data[i][1]['Heat Flow'].iloc[:len(big_data[i][0]['Heat Flow'])], color = st.session_state['shade'])
            else:
                ax1.fill_between(big_data[i][1][eje_x], big_data[i][0]['Heat Flow'].iloc[:len(big_data[i][1]['Heat Flow'])], big_data[i][1]['Heat Flow'], color = st.session_state['shade'])
    ax1.spines['top'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.yaxis.set_ticks([])
    ax1.tick_params(axis='y', which='both', length=0)
    
    with graf:
        st.pyplot(fig)


except FileNotFoundError:
    with graf:
        #st.title('Enter folder name')
        st.markdown('<p class="big-font">Enter Folder Name</p>', unsafe_allow_html=True)
#st.line_chart(data, x = 'Tr', y = 'Heat Flow')
