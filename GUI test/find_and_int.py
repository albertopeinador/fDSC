import numpy as np
import streamlit as st

def find_int_region(df_tuple, thold, y_name):
    dif = df_tuple[0][y_name] - df_tuple[1][y_name]
    max_diff_index = dif.idxmax()
    left_index = max_diff_index
    right_index = max_diff_index
    while left_index > 0 and dif.iloc[left_index] > thold:
        left_index -= 1

    while right_index < len(dif) - 1 and dif.iloc[right_index] > thold:
        right_index += 1

    int_data = df_tuple[0][y_name].iloc[left_index:right_index + 1] - df_tuple[1][y_name].iloc[left_index:right_index + 1]

    int_data = int_data.to_frame()
    int_data['t'] =  df_tuple[0]['t'].iloc[left_index:right_index + 1]
    return int_data, left_index, right_index

def integ(df, y_name, x_name):
    integral = np.trapz(df[y_name], df[x_name])
    return integral