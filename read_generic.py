import pandas as pd
import re
#import time

'''
def can_be_float(x):
    try:
        float(x)
        return True
    except ValueError:
        return False


def load_float_data(PATH, column_list, index = True, index_col = 0, reset_index = False):

    #start_time = time.time()
    df = pd.DataFrame(columns = column_list)

    with open(PATH, encoding = 'latin1') as file:
        for line in file:
            try:
                filtered_line = list(filter(can_be_float, re.split(r'\s+', line.replace(',', '.'))))
                float_line = list([float(i) for i in filtered_line])
                df.loc[len(df)] = float_line
            except ValueError:
                continue
    if index:
        df = df.set_index(column_list[index_col])
        print(df)
    if reset_index:
        dict_of_df = {}
        reset_points = df.index.to_series().diff().ne(1).cumsum()
        dataframes = [group for _, group in df.groupby(reset_points)]
        for i, df_part in enumerate(dataframes):
            dict_of_df[f'curva {i}'] = df_part
            print(f"DataFrame {i}:\n{df_part}\n")
        #end_time = time.time()
        #execution_time = end_time - start_time
        #print('Loading time: %.2f' % execution_time)
        return dict_of_df
    else:
        #end_time = time.time()
        #execution_time = end_time - start_time
        #print('Loading time: %.2f' % execution_time)
        return df
'''
'''if __name__ == '__main__':
    print(load_float_data('/Users/albpeivei/Desktop/XENG21 73282 coolings1 b282.txt', ['Index', 'Ts', 'Tr', 'Flow'], reset_index = True))

'''
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