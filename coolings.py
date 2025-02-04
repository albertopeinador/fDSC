import streamlit as st
import read_generic as read
import plotly.graph_objects as go
import pandas as pd
from io import StringIO

def coolingsWIP():
    st.markdown(
        """
        <div style="display: flex; justify-content: center; align-items: center; height: 100vh;">
            <h1 style="font-size: 50px; font-weight: bold; text-align: center;">COMING SOON</h1>
            <h2 style="font-size: 20px; text-align:center;">(now kinda for sure)</h2>
        </div>
        """,
        unsafe_allow_html=True
        )
    

def coolings():
    #st.title('Coolings data')
    uploaded_file = st.file_uploader("Upload a data file", type=["txt", "csv"], label_visibility='collapsed')
    curves, plots = st.columns([1.25, 5])
    fig = go.Figure()
    if 'uploaded_file' not in st.session_state:
        st.session_state['uploaded_file'] = None
        st.session_state['datas'] = None
        st.session_state['load_type'] = None
    with curves:
        index_reset = st.checkbox("Reset Index and Split Data", value = True)
    column_list = ["Index", "Ts", "Tr", "Value"]
    if uploaded_file is not None:
        with curves:
            status_box = st.status("Done!", expanded=False)
            if uploaded_file == st.session_state['uploaded_file'] and index_reset == st.session_state['load_type']:
                with status_box as status:
                    status.update(label="Done!", state="complete")
    if uploaded_file != st.session_state['uploaded_file'] or index_reset != st.session_state['load_type']:
        with curves:
            if uploaded_file is not None:
                with status_box as status:
                    st.session_state['datas'] = read.load_float_data(uploaded_file, column_list, index=True, index_col=0, reset_index=index_reset)
                    st.write()
                    status.update(label="Done!", state="complete")
        st.session_state['uploaded_file'] = uploaded_file
        st.session_state['load_type'] = index_reset
    if uploaded_file is not None:
        with curves:
            with status_box as status:
                if not index_reset:
                    st.dataframe(st.session_state['datas'])
                else:
                    for key, sub_df in st.session_state['datas'].items():
                        st.write(f"### {key}")
                        st.dataframe(sub_df)
    datas = st.session_state['datas']
    #st.write(type(datas))
    with curves:
        if uploaded_file is not None and index_reset:
            selected_keys = st.multiselect("Select DataFrames to include:", datas.keys(), default=datas.keys())
            filtered_dict = {key: datas[key] for key in selected_keys}
            if filtered_dict == {}:
                filtered_dict = datas
            #plot_curves = st.text_input(f'Plot Curves: (max index: {len(datas) - 1})', placeholder='Indexes of curves to plot, i.e. 1 3 5 ...').split()
            #if plot_curves == []:
            #    if index_reset:
            #        plot_curves = list(range(len(datas)))
            #plot_labels = [f'curva_{i}' for i in plot_curves]

    if uploaded_file is not None:
        with plots:
            if uploaded_file is not None:
                _, col, _ = st.columns([2.3, 2, 2])
                with col:
                    ejex = st.radio('Eje x', ['Ts', 'Tr'], horizontal=True)
                _, col2, _ = st.columns([1, 5, 1])
                with col2:
                    if index_reset:
                        for i in filtered_dict.keys():
                            fig.add_trace(go.Scatter(x = datas[i][ejex], y = datas[i]['Value']))
                    else:
                        fig.add_trace(go.Scatter(x = datas[ejex], y = datas['Value']))
                    st.plotly_chart(fig, use_container_width=True)
            with curves:
                _, dwl, _ = st.columns([.3, 1, .3])
                with dwl:
                    if index_reset:
                        df_list = []
                        id_row = []

                        for key, df in filtered_dict.items():
                            id_row.extend([key] * df.shape[1])  # Repeat key for each column
                            df_list.append(df)

                        # Concatenate along columns, aligning by index
                        result = pd.concat(df_list, axis=1)

                        # Insert the identifier row at the top
                        result.columns = pd.MultiIndex.from_arrays([id_row, result.columns])

                        csv_buffer = StringIO()
                        result.to_csv(csv_buffer, index=False)
                        csv_data = csv_buffer.getvalue()
                        st.download_button(
                                    label="Download CSV",
                                    data=csv_data,
                                    file_name="merged_data.csv",
                                    mime="text/csv"
                                )
                        #st.write(result)
