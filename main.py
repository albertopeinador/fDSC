import streamlit as st
import kinetics
import annealings

st.set_page_config(layout="wide")

options = ['kinetics', 'Annealings']

selected = st.selectbox('Choose an option', options, placeholder="Choose an option", label_visibility = 'collapsed')

if selected is not None:
    if selected == 'kinetics':
        kinetics.kinetics()
    
    elif selected == 'Annealings':
        annealings.annealings()