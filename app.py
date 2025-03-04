import streamlit as st

# from dashboard import  dashschedule, dashresults
from requirements import dashreqs
from architecture import sysarcfunc
from teststrategy import teststrat
from testfacility import testfacility
from testresults import testresults

st.set_page_config(page_title="Lego Rover Dashboard", page_icon="📡", layout="wide")

def main():

    st.header("🧩 Lego Rover Project Dashboard", divider="red")

    TABS = ["Test Facilities", "Requirements", "Architecture", "Test Strategy", "Test Results"]
    tabs = st.tabs(TABS)

    with tabs[0]:
        testfacility()
    with tabs[1]:
        dashreqs()
    with tabs[2]:
        sysarcfunc()
    with tabs[3]:
        teststrat()
    with tabs[4]:
        testresults()


if __name__ == "__main__":
    main()