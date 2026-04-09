import streamlit as st
import kinetics, annealings, welcome, coolings, step_response
import base64
import warnings
warnings.filterwarnings("ignore")
warnings.simplefilter("ignore")


def svg_to_base64(path: str) -> str:
    """Read an SVG file and return a base64-encoded data URI string."""
    with open(path, "rb") as f:
        svg_bytes = f.read()
    b64 = base64.b64encode(svg_bytes).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}"




st.set_page_config(layout="wide")

# st.markdown("""
# <style>
# /* Remove spacing around custom components */
# div[data-testid="stElementContainer"] {
#     margin-top: 0px !important;
#     margin-bottom: 0px !important;
#     padding: 0px !important;
# }

# /* Target the specific iframe container */
# iframe.stCustomComponentV1 {
#     margin: -10000px !important;
#     padding: 1em !important;
#     display: block;
# }

# /* Optional: remove extra gap from emotion wrapper */
# /*div[class^="st-emotion-cache"] {
#     margin: 0px !important;
#     padding: 0px !important;
# }*/
# </style>
# """, unsafe_allow_html=True)

# st.markdown("""
# <style>
# div[data-testid="stElementContainer"]:has(iframe[title="streamlit_js_eval.streamlit_js_eval"]) {
#     margin: 0 !important;
#     padding: 0 !important;
# }
# </style>
# """, unsafe_allow_html=True)


# --- Tab functions ---
def full_kin():
    with st.expander('Load Data', expanded=True):
        og_file = st.file_uploader(
            'Upload Files',
            accept_multiple_files=False,
            label_visibility='collapsed',
            type=['csv']
        )
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
            st.write("Enter curve names or use default by switching 'As table' toggle on.")
    else:
        st.write('Please Load File')

tabs = {
    "Welcome": welcome.welcome,
    "Kinetics": full_kin,
    "Annealings": annealings.annealings,
    "Coolings": coolings.coolings,
    "Step Response": step_response.step_res,
}

# --- Sidebar CSS ---
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            width: 4.2rem !important;   /* very narrow */
            min-width: 0rem !important;
        }
        .sidebar-icons {
            display: flex;
            flex-direction: column;
            justify-content: space-evenly;
            align-items: center;
            height: 200%;
        }
        .sidebar-icons img {
            width: 2.9rem;
            height: 2.9rem;
            margin: .5rem 0;
            cursor: pointer;
            
            transition: transform 0.2s ease;
        }
        .sidebar-icons img:hover {
            transform: scale(1.2);
        }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar nav with SVGs ---
icons = {
    "Welcome": "static/icons/welcome_icon.svg",
    "Annealings": "static/icons/anneal_icon.svg",
    "Step Response": "static/icons/step_icon.svg",
    "Kinetics": "static/icons/kinetic_icon.svg",
    "Coolings": "static/icons/cooling_icon.svg",
}

from streamlit_js_eval import get_geolocation, streamlit_js_eval

theme = streamlit_js_eval(
    js_expressions="window.matchMedia('(prefers-color-scheme: dark)').matches"
)


# Create placeholders for navigation
choice = st.sidebar.empty()

# Build custom HTML with clickable links
icon_html = '<div class="sidebar-icons">'
for tab in icons.keys():
    url = f"?nav={tab}"  # store selection in query params
    icon_path = icons[tab] if not theme else icons[tab][:-4] + '_dark' + '.svg'
    icon_b64 = svg_to_base64(icon_path)
    icon_html += f'<a href="{url}"><img src="{icon_b64}" title="{tab}"></a>'
icon_html += "</div>"

st.sidebar.markdown(icon_html, unsafe_allow_html=True)



# --- Detect selected tab ---
import urllib.parse

# when building the href:
href = f"?nav={urllib.parse.quote_plus(tab)}"

# when reading:
params = st.query_params
if 'nav' not in params:
    params['nav'] = 'Welcome'

tabs[params['nav']]()
