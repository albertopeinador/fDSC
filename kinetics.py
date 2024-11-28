import streamlit as st


def kinetics():
    og_file = st.file_uploader('Upload Files',
                               accept_multiple_files = False,
                               label_visibility = 'collapsed')
    