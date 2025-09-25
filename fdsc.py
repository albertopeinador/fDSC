import streamlit as st
# from streamlit_navigation_bar import st_navbar
import kinetics
import annealings
import welcome
import coolings
import step_response

st.set_page_config(layout="wide")

options = ['Welcome', 'Kinetics', 'Annealings', 'Coolings', 'Step Response']

# selected = st_navbar(options)

# if selected is not None:
#     if selected == 'Welcome':
#         welcome.welcome()
#     elif selected == 'Kinetics':
#         with st.expander('Load Data', expanded = True):
#             og_file = st.file_uploader('Upload Files',
#                                        accept_multiple_files = False,
#                                        label_visibility = 'collapsed',
#                                        type = ['csv'])
#             if og_file is not None:
#                 try:
#                     curvas = kinetics.get_names(og_file)
#                 except TypeError:
#                     st.write('Upload file please')
#         if og_file is not None:
#             try:
#                 df = kinetics.read_kinetics(og_file, curvas)
#                 kinetics.kinetics(df, og_file.name)
#             except NameError:
#                 st.write('Enter curve names or use default by switching \'As table\' toggle on.')
#         else:
#             st.write('Please Load File')
#     elif selected == 'Annealings':
#         annealings.annealings()
#     elif selected == 'Coolings':
#         coolings.coolings()
#     elif selected == 'Step Response':
#         step_response.step_res()


def full_kin():
    with st.expander('Load Data', expanded = True):
        og_file = st.file_uploader('Upload Files',
                                    accept_multiple_files = False,
                                    label_visibility = 'collapsed',
                                    type = ['csv'])
        if og_file is not None:
            try:
                curvas = kinetics.get_names(og_file)
            except TypeError:
                st.write('Upload file please')
    if og_file is not None:
        try:
            df = kinetics.read_kinetics(og_file, curvas)
            kinetics.kinetics(df, og_file.name)
        except NameError:
            st.write('Enter curve names or use default by switching \'As table\' toggle on.')
    else:
        st.write('Please Load File')

# ---- Sidebar Tiny Tab Switcher ----

# Set sidebar width using custom CSS
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            width: 1rem;
            min-width: 1rem;
        }
        [data-testid="stSidebar"] .css-1d391kg {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .sidebar-icon {
            font-size: 1.5rem;
            text-align: center;
            display: block;
            padding: 1rem 0;
        }
    </style>
""", unsafe_allow_html=True)

# Tab options: icon + name
tabs = {
    "Welcome": welcome.welcome,
    "Annealings": annealings.annealings,
    "Step Response": step_response.step_res,
    "Kinetics": full_kin,
    "Coolings":coolings.coolings
}

# Create tab switcher in sidebar using radio (icons only)
selection = st.sidebar.radio(
    label="",
    options=list(tabs.keys()),
    #format_func=lambda x: "",  # Hide label text
    index=0
)

# Run the selected tab function
tabs[selection]()
