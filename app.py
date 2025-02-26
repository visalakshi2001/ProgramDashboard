import streamlit as st

# from dashboard import  dashschedule, dashresults
from requirements import dashreqs
from architecture import sysarcfunc
from teststrategy import teststrat

st.set_page_config(page_title="CatSat Dashboard", page_icon="🛰️", layout="wide")

def main():

    st.header("🛰️ CubeSat Mission Dashboard", divider="red")

    TABS = ["Requirements", "Architecture", "Test Facilities", "Test Strategy", "Test Results"]
    tabs = st.tabs(TABS)

    with tabs[0]:
        dashreqs()
    with tabs[1]:
        sysarcfunc()
    with tabs[2]:
        st.write("Test Facilities")
    with tabs[3]:
        teststrat()


if __name__ == "__main__":
    main()