import streamlit as st
import pandas as pd

@st.cache_data
def kinetics():
    og_file = st.file_uploader('Upload Files',
                               accept_multiple_files = False,
                               label_visibility = 'collapsed',
                               type = ['csv'])
    names = ['time', 
                '3.45707',
                '2.71291',
                '2.13',
                '1.67',
                '1.31',
                '1.03',
                '0.81',
                '0.64',
                '0.5',
                '0.39238',
                '0.30792',
                '0.24165',
                '0.18963',
                '0.14882',
                '0.11679',
                '0.09165',
                '0.07192',
                '0.05644',
                '0.04429',
                '0.03476',
                '0.02728',
                '0.02141',
                '0.0168',
                '0.01318',
                '0.01035',
                '0.00812',
                '0.00637',
                '0.005']
    dataframe = pd.read_csv(og_file, sep=';', skiprows=2, names=names)
    dataframe = dataframe.map(lambda x: float(x.replace(',','.')))
    st.dataframe(dataframe)
    