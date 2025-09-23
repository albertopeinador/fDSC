import streamlit as st
import numpy as np
from scipy.optimize import curve_fit
import plotly.graph_objects as go
import pandas as pd

file = st.file_uploader('file')
fig = go.Figure
if file is not None:
    data = pd.read_csv(file, sep = '\s+', skipfooter=1, skiprows=2, encoding = 'latin1', dtype=str, names = ['Idx', 'HF', 't', 'Ts', 'Tr'])

    data = data.apply(lambda x: float(x.replace(',', '.')))
    x_axis = st.selectbox('x axis', data.columns())
    domain1 = st.number_input('domain start')
    domain2 = st.number_input('domain end')
    if not (domain1 and domain2):
        fig.add_trace(go.Scatter(x = data[x_axis], y = data['HF']))
    else:
        data = data[data[x_axis].between(domain1, domain2)]
        fig.add_trace(go.Scatter(x = data[x_axis], y = data['HF']))
        