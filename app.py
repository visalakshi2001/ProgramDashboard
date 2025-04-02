import streamlit as st
from supabase import create_client, Client
import json
import string
import pandas as pd

# from dashboard import  dashschedule, dashresults
from requirements import dashreqs
from architecture import sysarcfunc
from teststrategy import teststrat
from testfacility import testfacility
from testresults import testresults

from jsontocsv import json_to_csv

st.set_page_config(page_title="Lego Rover Dashboard", page_icon="📡", layout="wide")

def main():

    TABS = ["Test Facilities", "Requirements", "Architecture", "Test Strategy", "Test Results"]
    
    if st.button("🪄 Edit Data"):
        replace_data(TABS)

    st.header("🧩 Lego Rover Project Dashboard", divider="red")

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


@st.cache_resource
def init_connection():
    url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
    key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
    return create_client(url, key)

@st.dialog("Select a tab below and replace its data")
def replace_data(TABS):
    selected_tabs = st.multiselect("Choost the TAB(s) whose data you wish to replace:", options=TABS)

    data_ties = {
        TABS[0]: "TestFacilities",
        TABS[1]: "Requirements",
        TABS[2]: "SystemArchitecture",
        TABS[3]: "TestStrategy",
        TABS[4]: "TestResults",
    }

    required_files = [data_ties[tab] + ".json" for tab in selected_tabs]
    new_files = st.file_uploader(accept_multiple_files=True, label="Upload CSV Files listed below")

    uploaded_file_names = [f.name.split(".json")[0].strip().translate({ord(ch): None for ch in '0123456789'}).strip() + ".json"
                            for f in new_files]
    all_files_uploaded = all(f in uploaded_file_names for f in required_files)
    
    for f in new_files:
        file_contents = f.read()
        try:
            response = (conn.storage
                        .from_("legorover")
                        .upload(
                            file=file_contents,
                            path="reports/" + f.name,
                            file_options={"upsert": "true"}
                        ))
        except:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("Poblem uploading new files()")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        
        if response:
            st.success(f"✅ {f.name} uploaded successfully!")
            csv_op_file_name = f.name.split(".json")[0].strip().translate({ord(ch): None for ch in '0123456789'}).strip() + ".csv"
            json_to_csv(json_file_object=file_contents, csv_output_path="reports/" + csv_op_file_name)
            st.success(f"✅ {csv_op_file_name} saved to repository")
    
    if selected_tabs!= [] and all_files_uploaded:
        st.write("✅ All required files have been uploaded!")
        st.write("🔁 Rerun page to view changes or press 'Done' button")
    else:
        missing_files = [file for file in required_files if file not in uploaded_file_names]
        if missing_files:
            st.warning(f"Missing files: {', '.join(missing_files)}")
    
    if st.button("Done"):
        st.rerun(scope="app")


if __name__ == "__main__":

    if "conn" not in st.session_state:
        st.session_state["conn"] = None
    conn = init_connection()
    st.session_state["conn"] = conn
    main()

