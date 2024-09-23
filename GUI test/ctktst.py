import streamlit as st
import matplotlib.pyplot as plt

st.write('hello world')

cutoff = st.slider('cutoff')

st.text_input('Folder Name', key = 'dir')

print(st.session_state.dir)