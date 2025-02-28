import streamlit as st



def issuesinfo():

    cont = st.container(border=True)

    cont.markdown("<h4>Warnings/Issues</h4>", True)


    cont.warning("The test duration is more than 60 days", icon="⚠️")

    cont.error("The Equipment VT_Stopwatch for Test Case T2_1 is not available at the assigned facility UA_TestFacility", icon="❗")
    cont.error("The Researcher UA_Researcher for Test Case T3_3 is not available at the assigned facility VT_TestFacility", icon="❗")