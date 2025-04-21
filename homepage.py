import streamlit as st
import pandas as pd

from jsontocsv import json_to_csv

def homepageview(TABS):

    try:
        triplecount = pd.read_csv("reports/TripleCount.csv")
        cntval = triplecount["tripleCount"].iloc[0]
    except:
        st.toast("TrippleCount.csv is not uploaded correctly", icon="🚨")
        savefilename = filename = "TripleCount.json"
        try:
            conn = st.session_state["conn"]
            with open(f"reports/{savefilename}", "wb+") as f:
                    response = (
                        conn.storage
                        .from_("legorover")
                        .download(f"reports/{filename}")
                    )
                    f.write(response)
            csv_op_file_name = filename.split(".json")[0].strip().translate({ord(ch): None for ch in '0123456789'}).strip() + ".csv"
            json_to_csv(json_input_path=f"reports/{savefilename}", csv_output_path="reports/" + csv_op_file_name)
        except:
            print(f"{filename} is either missing or corrupted upload it to cloud and restart the app")
        
        triplecount = pd.read_csv("reports/TripleCount.csv")
        cntval = triplecount["tripleCount"].iloc[0]
    

    st.markdown(f"#### RDF Triple Count: :blue[{cntval}]", unsafe_allow_html=True)


    st.markdown(f"#### Files used in each tab", unsafe_allow_html=True)
    data_ties = {
        TABS[0]: ["TripleCount"],
        TABS[1]: ["TestFacilities"],
        TABS[2]: ["Requirements"],
        TABS[3]: ["SystemArchitecture", "MissionArchitecture"],
        TABS[4]: ["TestStrategy"],
        TABS[5]: ["TestResults"],
    }

    st.dataframe(pd.DataFrame(data={
                                "Tab Name": [key for key, values in data_ties.items() for _ in values],
                                "Files Utilized": [f"{item}.json" for values in data_ties.values() for item in values]
                                }),
             hide_index=True, width=500)

    
    

    