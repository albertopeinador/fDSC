import streamlit as st
from streamlit_navigation_bar import st_navbar
import kinetics
import annealings

st.set_page_config(layout="wide")

options = ['kinetics', 'Annealings']

selected = st_navbar(['kinetics', 'Annealings'])
#selected = st.selectbox('Choose an option', options, placeholder="Choose an option", label_visibility = 'collapsed')

if selected is not None:
    if selected == 'kinetics':
        kinetics.kinetics()
    
    elif selected == 'Annealings':
        annealings.annealings()