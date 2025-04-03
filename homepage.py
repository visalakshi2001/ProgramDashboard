import streamlit as st
import pandas as pd

def homepageview(TABS):

    triplecount = pd.read_csv("reports/TripleCount.csv")
    cntval = triplecount["tripleCount"].iloc[0]

    st.markdown(f"#### RDF Triple Count: :blue[{cntval}]", unsafe_allow_html=True)


    st.markdown(f"#### Files used in each tab", unsafe_allow_html=True)
    data_ties = {
        TABS[0]: "TripleCount",
        TABS[1]: "TestFacilities",
        TABS[2]: "Requirements",
        TABS[3]: "SystemArchitecture",
        TABS[4]: "TestStrategy",
        TABS[5]: "TestResults",
    }

    st.dataframe(pd.DataFrame(data={"Files Utilized": map(lambda x: x+".json", list(data_ties.values())), "Tab Name": data_ties.keys()}),
             hide_index=True, width=500)
    
    

    