import streamlit as st
import pandas as pd
import re

from issueswarnings import issuesinfo

# ########## REQUIREMENTS VIEW FUNCTION
def dashreqs():

    breakdown = pd.read_csv("reports/Requirements.csv")
    st.subheader("Requirements Table", divider="orange")

    requirement_columns = breakdown.columns.to_series()

    requirement_columns = requirement_columns.apply(lambda y: re.sub("\s{2,}", " ", y))
    requirement_columns = requirement_columns.apply(lambda y: ''.join(map(lambda x: x if x.islower() else " "+x, y)).strip())

    requirement_columns = requirement_columns.apply(lambda y: re.sub("\s{2,}", " ", y))
    requirement_columns = requirement_columns.apply(lambda y: re.sub("(Req)\s", "Requirement ", y))

    breakdown.columns = requirement_columns

    cols = st.columns([0.7,0.3])

    with cols[0]:
        st.dataframe(breakdown, hide_index=True, use_container_width=True)
    
    with cols[1]:
        issuesinfo(curr_tab="requirements")
    

   