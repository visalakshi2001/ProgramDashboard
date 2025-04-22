import streamlit as st
import pandas as pd
import re

from issueswarnings import issuesinfo
from jsontocsv import json_to_csv, validate_csv

def dashreqsvalidate():
    expected_cols = [ "ReqID" , "ReqName" , "ReqDescription" , "ReqSubject" , "SatisfiedBy" , "VerifiedBy" ]
    is_valid = validate_csv("reports/Requirements.csv", expected_cols)
    if not is_valid:
        st.toast("Requirements.csv is not uploaded correctly", icon="🚨")
        savefilename = filename = "Requirements.json"
        try:
            conn = st.session_state["conn"]
            with open(f"reports/{savefilename}", "wb+") as f:
                    response = (
                        conn.storage
                        .from_("legorover")
                        .download(f"reports_full/{filename}")
                    )
                    f.write(response)
            csv_op_file_name = filename.split(".json")[0].strip().translate({ord(ch): None for ch in '0123456789'}).strip() + ".csv"
            json_to_csv(json_input_path=f"reports/{savefilename}", csv_output_path="reports/" + csv_op_file_name)
        except:
            print(f"{filename} is either missing or corrupted upload it to cloud and restart the app")
    else:
        dashreqs()

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
        st.markdown("<h4>Warnings/Issues</h4>", True)
        try:
            issuesinfo(curr_tab="requirements")
        except:
            st.write("There is an internal error in displaying the test warnings")

   