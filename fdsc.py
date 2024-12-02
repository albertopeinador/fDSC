import streamlit as st
from streamlit_navigation_bar import st_navbar
import kinetics
import annealings
import welcome

st.set_page_config(layout="wide")

options = ['Welcome', 'Kinetics', 'Annealings', 'Coolings']

selected = st_navbar(options)
#selected = st.selectbox('Choose an option', options, placeholder="Choose an option", label_visibility = 'collapsed')

if selected is not None:
    if selected == 'Welcome':
        welcome.welcome()
    elif selected == 'Kinetics':
        with st.expander('Load Data'):
            og_file = st.file_uploader('Upload Files',
                                       accept_multiple_files = False,
                                       label_visibility = 'collapsed',
                                       type = ['csv'])
            try:
                curvas = kinetics.get_names(og_file)
            except TypeError:
                st.write('Upload file please')
        try:
            df = kinetics.read_kinetics(og_file, curvas)
            kinetics.kinetics(df)
        except NameError:
            st.write('Enter curve names or use default by switching \'As table\' toggle on.')
    elif selected == 'Annealings':
        annealings.annealings()