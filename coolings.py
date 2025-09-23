import streamlit as st
import Assets.read_generic as read
import plotly.graph_objects as go
import pandas as pd
from io import StringIO

#def coolingsWIP():
#    st.markdown(
#        """
#        <div style="display: flex; justify-content: center; align-items: center; height: 100vh;">
#            <h1 style="font-size: 50px; font-weight: bold; text-align: center;">COMING SOON</h1>
#            <h2 style="font-size: 20px; text-align:center;">(now kinda for sure)</h2>
#        </div>
#        """,
#        unsafe_allow_html=True
#        )


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
                _, x_ax, selector, slider = st.columns([.8, 1, 1, 3])
                with x_ax:
                    ejex = st.radio('Eje x', ['Ts', 'Tr'], horizontal=True)
                with selector: 
                    selected = st.selectbox('Modify: ', filtered_dict.keys())
                #with slider:
                    #delta = st.slider('apply delta: ', max_value=1., min_value=-1., value=0., step=.01)
                _, col2, _ = st.columns([1, 6, 1])
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
        for i in filtered_dict.keys():
            if f"new_delta_{i}" not in st.session_state:
                st.session_state[f"new_delta_{i}"] = 0.
            if f"delta_{i}" not in st.session_state:
                st.session_state[f"delta_{i}"] = 0.
        if f'has_changed_{selected}' not in st.session_state:
            st.session_state[f'has_changed_{selected}'] = True
        if st.session_state[f"new_delta_{selected}"] != 0.:
            st.session_state[f"delta_{selected}"] = st.session_state[f"new_delta_{selected}"]
            st.session_state[f'has_changed_{selected}'] = False
        elif st.session_state[f'has_changed_{selected}']:
            st.session_state[f"delta_{selected}"] = st.session_state[f"new_delta_{selected}"]

        with plots:
            with slider:
                current_delta = st.slider(
                    f"Set the delta of Ta = {selected}",
                    min_value=-1.0,
                    max_value=1.0,
                    key=f"new_delta_{selected}",
                    value=st.session_state[f"delta_{selected}"],
                    step = .01
                )
                #st.write(st.session_state[f"delta_{Ta}"])

        
            #   INTEGRATION LOOP
        mod_filtered_dict = {}
        fig2 = go.Figure()
        for i in filtered_dict.keys():
            if f"delta_{i}" in st.session_state:
                #   Apply delta modification to all curves
                mod_filtered_dict[i] = filtered_dict[i]
                mod_filtered_dict[i]["Value"] += (st.session_state[f"delta_{i}"]) * mod_filtered_dict[i]["Value"].max()
            fig2.add_trace(go.Scatter(x = mod_filtered_dict[i][ejex], y = mod_filtered_dict[i]['Value']))
        st.plotly_chart(fig2, use_container_width=True)
            #st.line_chart(mod_filtered_dict, x = ejex, y=filtered_dict[i]['Value'])
                        #st.write(result)
