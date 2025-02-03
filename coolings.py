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
    st.title('Coolings data')
    uploaded_file = st.file_uploader("Upload a data file", type=["txt", "csv"])
    index_reset = st.checkbox("Reset Index and Split Data")
    if uploaded_file is not None:
        with st.status("Processing...", expanded=True) as status:
            if not index_reset:
                column_list = ["Index", "Ts", "Tr", "Value"]  # Adjust column names accordingly
                df = read.load_float_data(uploaded_file, column_list, index=True, index_col=0, reset_index=False)
                st.write("Processed Data:")
                st.dataframe(df)

            # Optionally handle reset index
            else:
                split_data = read.load_float_data(uploaded_file, column_list, index=True, index_col=0, reset_index=True)
                for key, sub_df in split_data.items():
                    st.write(f"### {key}")
                    st.dataframe(sub_df)
            status.update(label="Done!", state="complete")