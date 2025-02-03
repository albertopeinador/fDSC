import streamlit as st
import read_generic as read
import pandas as pd
import re

def coolingsWIP():
    st.markdown(
        """
        <div style="display: flex; justify-content: center; align-items: center; height: 100vh;">
            <h1 style="font-size: 50px; font-weight: bold; text-align: center;">COMING SOON</h1>
            <h2 style="font-size: 20px; text-align:center;">(now kinda for sure)</h2>
        </div>
        """,
        unsafe_allow_html=True
        )
    

def coolings():
    #st.title('Coolings data')
    uploaded_file = st.file_uploader("Upload a data file", type=["txt", "csv"], label_visibility='collapsed')
    curves, plots = st.columns([2.1, 5])
    if 'uploaded_file' not in st.session_state:
        st.session_state['uploaded_file'] = None
        st.session_state['datas'] = None
    with curves:
        index_reset = st.checkbox("Reset Index and Split Data")
    column_list = ["Index", "Ts", "Tr", "Value"]
    if uploaded_file is not None:
        with curves:
            status_box = st.status("Processing...", expanded=False)
    if uploaded_file != st.session_state['uploaded_file']:
        with curves:
            if uploaded_file is not None:
                with status_box as status:
                    st.session_state['datas'] = read.load_float_data(uploaded_file, column_list, index=True, index_col=0, reset_index=index_reset)

                    status.update(label="Done!", state="complete")
        st.session_state['uploaded_file'] = uploaded_file
    if uploaded_file is not None:
        with curves:
            with status_box as status:
                if not index_reset:
                    st.dataframe(st.session_state['datas'])
                else:
                    for key, sub_df in st.session_state['datas'].items():
                        st.write(f"### {key}")
                        st.dataframe(sub_df)
    with plots:
        if uploaded_file is not None:
            _, col, _ = st.columns([2.3, 2, 2])
            with col:
                st.radio('Eje x', ['Ts', 'Tr', 't'], horizontal=True)