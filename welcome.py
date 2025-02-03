import streamlit as st

def welcome():
    st.markdown("""
        <div style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: #f9f9f9;">
            <div style="width: 80%; margin: auto; padding-top: 20px;">
                <div style="font-size: 3em; color: #333; text-align: center; margin-bottom: 20px;">
                    JM / F-DSC
                </div>
                <div style="font-size: 1.3em; text-align:center; color: #555; margin-bottom: 20px;">
                    Our Data Processing Tool for Flash Differential Scanning Calorimetry (a.k.a Fast Differential Calorimetry)
                </div>
                <div style="font-size: 1em; color: #666; text-align: justify;">
                    <p>
                        Welcome! This program is designed to assist with processing data for <span style="font-weight: bold; color: #0073e6;">Flash Differential Scanning Calorimetry</span> (FDSC).
                        You can explore the various tools available by navigating through the tabs at the top of the page.
                        These tabs provide access to different types of measurements we currently support—although please note that most are still a work in progress (WIP).
                    </p>
                    <p>
                        Below, you will find detailed instructions on how to use these tools, as well as information on their capabilities.
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
