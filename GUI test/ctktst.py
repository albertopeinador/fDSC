import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.offline import iplot
import pandas as pd

st.write('hello world')

dfs = {'df1':pd.DataFrame({'a':[1, 2, 4, 5], 'b':[2, 4, 6, 8]}), 'df2':pd.DataFrame({'a':[2, 3, 6, 7], 'b':[3, 2, 5, 3]})}

fig = go.Figure()

for i in dfs:
        fig = fig.add_trace(go.Scatter(x = dfs[i]["a"], y = dfs[i]["b"], name = i))
fig