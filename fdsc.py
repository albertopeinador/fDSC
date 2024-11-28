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
        kinetics.kinetics()
    elif selected == 'Annealings':
        annealings.annealings()