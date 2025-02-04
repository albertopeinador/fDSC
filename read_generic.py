import pandas as pd
import re
#import time


def can_be_float(x):
    try:
        float(x)
        return True
    except ValueError:
        return False

def load_float_data(file, column_list, index=True, index_col=0, reset_index=False):
    df = pd.DataFrame(columns=column_list)
    
    content = file.getvalue().decode("latin1")
    for line in content.splitlines():
        try:
            filtered_line = list(filter(can_be_float, re.split(r'\s+', line.replace(',', '.'))))
            float_line = [float(i) for i in filtered_line]
            df.loc[len(df)] = float_line
        except ValueError:
            continue
    
    if index:
        df = df.set_index(column_list[index_col])
    
    if reset_index:
        dict_of_df = {}
        reset_points = df.index.to_series().diff().ne(1).cumsum()
        dataframes = [group for _, group in df.groupby(reset_points)]
        for i, df_part in enumerate(dataframes):
            dict_of_df[f'curva_{i}'] = df_part
        return dict_of_df
    
    return df