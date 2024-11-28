import streamlit as st
from streamlit_navigation_bar import st_navbar
import kinetics
import annealings

st.set_page_config(layout="wide")

options = ['Welcome', 'Kinetics', 'Annealings', 'Coolings']

selected = st_navbar(['kinetics', 'Annealings'])
#selected = st.selectbox('Choose an option', options, placeholder="Choose an option", label_visibility = 'collapsed')

if selected is not None:
    if selected == 'Welcome':
        st.write('Welcome to our data processing program for flash diferencial scanning calorimetry (or fast diferencia calorimetry).\nUp top you will find different tabs for the different types of measurements we currently support (most are WIP still). You can see below instructions and details on how to use these tools and what they are capable of.')
    elif selected == 'kinetics':
        kinetics.kinetics()
    
    elif selected == 'Annealings':
        annealings.annealings()