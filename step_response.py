import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy.fft import fft
from scipy.signal import savgol_filter
from io import StringIO
import csv


def derive(x, y):
    x = np.asarray(x)
    y = np.asarray(y)
    dy_dx = np.zeros_like(y)
    dy_dx[1:-1] = (y[2:] - y[:-2]) / (x[2:] - x[:-2])
    dy_dx[0] = (y[1] - y[0]) / (x[1] - x[0])
    dy_dx[-1] = (y[-1] - y[-2]) / (x[-1] - x[-2])
    return dy_dx



def get_window(df, window_index, window_size):
    start = window_index * window_size
    end = start + window_size
    return df.iloc[start:end].reset_index(drop=True), start, end


def step_res():

    curves,plot1, plot2 = st.columns([1, 1, 1])
    with curves:
        uploaded_file = st.file_uploader("Upload a data file", type=["txt"], label_visibility='collapsed')

        num_of_harmonics = st.number_input('Number of frequencies to plot:', value=5)
        type_of_cp = st.selectbox('Type of Cp to plot:', ['Reversible', 'Irreversible'])

        smooth_window = st.number_input('Smooth_window', value = 10)
        poly_order = st.number_input('Smooth_polynomial order', value=4)

    fig = go.Figure()
    fig2 = go.Figure()
    if 'uploaded_file' not in st.session_state:
        st.session_state['uploaded_file'] = None
        st.session_state['datas'] = None
        st.session_state['load_type'] = None

    column_list = ['Index', 't', 'HF', 'Ts', 'Tr']
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file,  sep = r'\s+', skiprows=2, skipfooter=1, names = column_list, 
                    encoding="ISO-8859-1", engine='python', on_bad_lines='skip', decimal=',', index_col='Index')
        for col in data.columns:
            try:
                data[col] = data[col].str.replace(",", ".", regex=False).astype(float)
            except:
                pass

        diff = data['Tr'].diff()

            #   Getting experiment parameters from measurement

        POINTS_PER_RAMP = diff[(diff == 0) & (diff.shift(1) > 0)].index[0] - 1
        STEP_WINDOW_SIZE = diff[(diff > 0) & (diff.shift(1) == 0)].index[0] - 1
        START_TEMP = data['Tr'][STEP_WINDOW_SIZE]
        END_TEMP = data['Tr'][len(data['Tr'])-1]
        TEMP_STEP = np.abs(data['Tr'][int(1.9*STEP_WINDOW_SIZE)] - START_TEMP)
        NUM_OF_WINDOWS = len(data['Tr']) // STEP_WINDOW_SIZE
        BASE_FREQ = 1. / (data['t'][STEP_WINDOW_SIZE] - data['t'][POINTS_PER_RAMP])


        #   SUBSTRACT BASELINE

        for wdw_indx in range(NUM_OF_WINDOWS):
            wdw_data, start_idx, end_idx = get_window(data, wdw_indx, STEP_WINDOW_SIZE)
            base_val = wdw_data['HF'][len(wdw_data)-200:].mean()
            
            data.loc[start_idx:end_idx, 'HF'] -= base_val

        heat_rate = derive(data['t'].values, data['Ts'].values)


        Cp_tot = []
        Cp_rev = []
        Cp_irev = []
        total_Cp = []
        heat_rate_df = pd.DataFrame({'beta':heat_rate})
        for wdw_indx in range(NUM_OF_WINDOWS):

            wdw_data, start_idx, end_idx = get_window(data, wdw_indx, STEP_WINDOW_SIZE)
            wdw_q, _,_ = get_window(heat_rate_df, wdw_indx, STEP_WINDOW_SIZE)

            # fft_freq = fftfreq(STEP_WINDOW_SIZE, wdw_data['t'][1] - wdw_data['t'][0])
            hf_fft = fft(wdw_data['HF'], n=STEP_WINDOW_SIZE)
            beta_fft = fft(wdw_q['beta'], n=STEP_WINDOW_SIZE)
            total_Cp.append( np.real(hf_fft[0] / beta_fft[0]) )
            Cp_tot.append( hf_fft / beta_fft )
            Cp_rev.append(np.real(hf_fft / beta_fft))
            Cp_irev.append(np.imag(hf_fft / beta_fft))
            T = np.linspace(START_TEMP, END_TEMP, NUM_OF_WINDOWS)
        fig.add_trace(
                        go.Scatter(
                            x=T,
                            y=total_Cp,
                            #line_color=color_list[i],
                            mode="lines",
                            #line = dict(color = 'blue', ),
                            name = "Total Cp"
                        )
                    )
        plot_data = [T, total_Cp]
        plot_data_header = ['T','Total Cp']

        total_Cp = savgol_filter(total_Cp, smooth_window, poly_order)
        total_Cp_deriv = derive(T, total_Cp)

        deriv_data = [T, total_Cp]
        deriv_data_header = ['T','Total Cp']

        fig2.add_trace(
            go.Scatter(
                x=T,
                y=total_Cp_deriv,
                #line_color=color_list[i],
                mode="lines",
                name = f'Total Cp'
            )
            )
        
        for har in range(num_of_harmonics):
            har += 1
            omega_cp = [Cp_rev[i][har] for i in range(len(Cp_rev))] if type_of_cp == 'Reversible' else [-Cp_irev[i][har] for i in range(len(Cp_rev))]
            fig.add_trace(
            go.Scatter(
                x=T,
                y=omega_cp,
                #line_color=color_list[i],
                mode="lines",
                name = f'{har*BASE_FREQ:.2f} Hz'
            )
            )
            plot_data.append(omega_cp)
            plot_data_header.append(f'{har*BASE_FREQ:.2f} Hz')
            omega_cp = savgol_filter(omega_cp, smooth_window, poly_order)
            deriv = derive(T, omega_cp)
            fig2.add_trace(
            go.Scatter(
                x=T,
                y=deriv,
                #line_color=color_list[i],
                mode="lines",
                name = f'{har*BASE_FREQ:.2f} Hz'
            )
            )
            deriv_data.append(deriv)
            deriv_data_header.append(f'{har*BASE_FREQ:.2f} Hz')
        rows = list(zip(*plot_data))
        csv_buffer = StringIO()
        csv_writer = csv.writer(csv_buffer, quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(plot_data_header)
        csv_writer.writerows(rows)
        csv_text = csv_buffer.getvalue()
        csv_buffer.close()


        rows_deriv = list(zip(*deriv_data))
        csv_buffer_deriv = StringIO()
        csv_writer_deriv = csv.writer(csv_buffer_deriv, quoting=csv.QUOTE_MINIMAL)
        csv_writer_deriv.writerow(deriv_data_header)
        csv_writer_deriv.writerows(rows_deriv)
        csv_text_deriv = csv_buffer_deriv.getvalue()
        csv_buffer_deriv.close()

        fig.update_layout(
            title = f"{type_of_cp} Cp",
            yaxis_title = "Cp",
            xaxis_title = 'T'
            )
        fig2.update_layout(
            title = f"Derivative of {type_of_cp} Cp",
            yaxis_title = "dCp / dT",
            xaxis_title = 'T',
            xaxis=dict(visible=True),
            yaxis=dict(visible=True),
            )
        with plot1:
            st.plotly_chart(fig, use_container_width = True)
            st.download_button(label="Download Cp CSV",
                                data=csv_text,                # <-- plain string is fine
                                file_name=f"{uploaded_file.name}_Cp_data.csv",
                                mime="text/csv",
                            )
        with plot2:
            st.plotly_chart(fig2, use_container_width = True)
            st.download_button(label="Download Derivative CSV",
                                data=csv_text_deriv,                # <-- plain string is fine
                                file_name=f"{uploaded_file.name}_Cp_derivative_data.csv",
                                mime="text/csv",
                            )

        
    #     with curves:
    #         status_box = st.status("Done!", expanded=False)
    #         if uploaded_file == st.session_state['uploaded_file']:
    #             with status_box as status:
    #                 status.update(label="Done!", state="complete")
    # if uploaded_file != st.session_state['uploaded_file']:
    #     with curves:
    #         if uploaded_file is not None:
    #             with status_box as status:
    #                 st.session_state['datas'] = read.load_float_data(uploaded_file, column_list, index=True, index_col=0)
    #                 st.write()
    #                 status.update(label="Done!", state="complete")
    #     st.session_state['uploaded_file'] = uploaded_file


    # data = st.session_state['datas']
    # inputs, plots = st.columns([ 1, 4])
    # Ts = data['Ts'].values
    # t = data['t'].values
    # dTs_dt = derive(t, Ts)

    # data['q'] = dTs_dt

    # data['baseline']=np.zeros_like(Ts)

    # # Keep only the relevant columns for further analysis
    # data = data[['t', 'Ts','baseline', 'HF', 'q']]

    # r = len(data)

    # # input_file = st.file_uploader("Upload a data file", type=["txt", "csv"], label_visibility='collapsed')
    # with inputs:
    #     basefreq = st.number_input('Base Frequency', value = 10)
    #     w_width = st.number_input('Number of points per step', value = 1024)
    #     offset = st.number_input('Window offset', value = 0)
    # k = int(r / w_width)
    # baselines = []
    # results = pd.DataFrame()
    # for col in ['t', 'Ts']:
    #     col_results = []
    #     for i in range(k):
    #         start = offset + i * w_width
    #         end = start + w_width - offset
    #         avg = data[col][start:end].mean()    
    #         col_results.append(avg)
    #     results[col] = col_results

    # with plots:
    #     st.write(results)

    # if 'uploaded_file' not in st.session_state:
    #     st.session_state['uploaded_file'] = None
    #     st.session_state['datas'] = None
    #     st.session_state['load_type'] = None
    # try:
    #     data = read.load_float_data(input_file, ['Index', 't', 'HF', 'Ts', 'Tr'])
    #     st.write('Hello')
    #     st.write(data)
    # except Exception as e:
    #     st.write(e)
