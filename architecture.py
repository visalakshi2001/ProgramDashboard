import streamlit as st
import pandas as pd

# for making UML diagrams
import graphviz

from jsontocsv import validate_csv, json_to_csv

# def sysarcvaliate():

#     expected_cols_sys = [ "SOI" , "Subsystem" , "Component" ]
#     expected_cols_miss = [ "Mission" , "Env" , "MissionEntities" ]
#     is_valid_sys = validate_csv("reports/TestResults.csv", expected_cols_sys, skip_non_null_check=True)
#     is_valid_miss = validate_csv("reports/TestResults.csv", expected_cols_miss, skip_non_null_check=True)

#     st.write(is_valid_sys, is_valid_miss)

#     if not is_valid_sys:
#         st.toast("SystemArchitecture.csv is not uploaded correctly", icon="🚨")
#         savefilename = filename = "SystemArchitecture.json"
#         try:
#             conn = st.session_state["conn"]
#             with open(f"reports/{savefilename}", "wb+") as f:
#                     response = (
#                         conn.storage
#                         .from_("legorover")
#                         .download(f"reports_full/{filename}")
#                     )
#                     f.write(response)
#             csv_op_file_name = filename.split(".json")[0].strip().translate({ord(ch): None for ch in '0123456789'}).strip() + ".csv"
#             json_to_csv(json_input_path=f"reports/{savefilename}", csv_output_path="reports/" + csv_op_file_name)
#         except:
#             print(f"{filename} is either missing or corrupted upload it to cloud and restart the app")
    
#     if not is_valid_miss:
#         st.toast("MissionArchitecture.csv is not uploaded correctly", icon="🚨")
#         savefilename = filename = "MissionArchitecture.json"
#         try:
#             conn = st.session_state["conn"]
#             with open(f"reports/{savefilename}", "wb+") as f:
#                     response = (
#                         conn.storage
#                         .from_("legorover")
#                         .download(f"reports_full/{filename}")
#                     )
#                     f.write(response)
#             csv_op_file_name = filename.split(".json")[0].strip().translate({ord(ch): None for ch in '0123456789'}).strip() + ".csv"
#             json_to_csv(json_input_path=f"reports/{savefilename}", csv_output_path="reports/" + csv_op_file_name)
#         except:
#             print(f"{filename} is either missing or corrupted upload it to cloud and restart the app")
    
#     if not (is_valid_miss or is_valid_sys):
#         st.toast("Please populate the System or Mission Architecture with correct data and re-upload")
#     else:
#         sysarcfunc()

# ########## ARCHITECTURE VIEW FUNCTION
def sysarcfunc():
    # read the data for the architecture
    system = pd.read_csv("reports/SystemArchitecture.csv")
    mission = pd.read_csv("reports/MissionArchitecture.csv")

    # Make a dropdown selection menu, with a title, and list of options. 
    # this component returns the variable that is selected
    graphchoice = st.selectbox("Select view", ["System Architecture", "Mission Architecture"], index=0)

    # initiate a empty diagraph
    dot = graphviz.Digraph(comment='Hierarchy', strict=True)

    cols = st.columns(2)
    
    if graphchoice == "System Architecture":
        # st.dataframe(system)
        for index, row in system.iterrows():
            soi = row["SOI"]
            subsys = row["Subsystem"]
            comp = row["Component"]

            if pd.notna(soi):
                dot.node(soi)

            if pd.notna(subsys):
                if subsys not in dot.body:
                    dot.node(subsys)
                if pd.notna(soi):
                    dot.edge(soi, subsys, label="has subsystem")
            
            if pd.notna(comp):
                if comp not in dot.body:
                    dot.node(comp,)
                if pd.notna(subsys):
                    dot.edge(subsys, comp, label="has subject")  
        cols[0].graphviz_chart(dot, True)
    
    elif graphchoice == "Mission Architecture":
        for index, row in  mission.iterrows():
            mission = row["Mission"]
            env = row["Env"]
            missent = row["MissionEntities"]

            dot.node(mission)

            if pd.notna(env):
                if env not in dot.body:
                    dot.node(env)
                dot.edge(mission, env, label="has environment")
            if pd.notna(missent):
                dot.node(missent)
                # dot.edge(missname, misscomp, arrowhead="diamond", label="has component")
                dot.edge(env, missent, label="has entity")

        cols[0].graphviz_chart(dot, True)
    




