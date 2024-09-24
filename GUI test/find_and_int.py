import pandas as pd
import scipy.integrate as sc

def find_int_region(df_tuple, thold, y_name):
    dif = df_tuple[0][y_name] - df_tuple[1][y_name]
    max_diff_index = dif.idxmax().values[0]
    left_index = max_diff_index
    right_index = max_diff_index
    while left_index > 0 and dif.iloc[left_index].values[0] > thold:
        left_index -= 1

    while (right_index < len(df_tuple[0][y_name]) - 1 or right_index < len(df_tuple[1][y_name])) and dif.iloc[right_index].values[0] > thold:
        right_index += 1

    int_data = df_tuple[0].iloc[left_index:right_index + 1] - df_tuple[1].iloc[left_index:right_index + 1]

    return int_data