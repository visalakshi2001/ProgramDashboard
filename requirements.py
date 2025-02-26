import streamlit as st
import pandas as pd


# ########## REQUIREMENTS VIEW FUNCTION
def dashreqs():
    st.subheader("Requirements Table", divider="orange")
    breakdown = pd.read_csv("reports/Requirements.csv")
    st.dataframe(breakdown, hide_index=True, use_container_width=True)
    
    # cont = st.container(border=True)
    # cont.subheader("Warnings")
    # for _, row in breakdown.iterrows():
    #     req = row["ReqName"]
    #     verified = row["Verified By"]
    #     satisfied = row["Satisfied By"]
    #     # result = row["Results"]
    #     # status = row["Verification Status"]

    #     if pd.isna(verified):
    #         cont.warning(f"Requirement {req} is not verified by any analysis", icon="⚠️")
    #     if pd.isna(satisfied):
    #         cont.warning(f"Requirement {req} is not satisfied by any mission element", icon="⚠️")
    #     # if pd.notna(verified) and status != "PASS":
    #     #     cont.error(f"Requirement {req} has not PASSED the analysis")

    # req_choice = st.selectbox("Select Requirement by Name", options=breakdown["Requirement Name"], index=1)
    # target_req = breakdown[breakdown["Requirement Name"] == req_choice]

    # dot = graphviz.Digraph(comment='Hierarchy', strict=True)
    # for _, row in target_req.iterrows():
            
    #     reqid = row["Requirement ID"]
    #     req = row["Requirement Name"]
    #     verified = row["Verified By"]
    #     satisfied = row["Satisfied By"]
    #     # result = row["Results"]
    #     # status = row["Verification Status"]

    #     if pd.notna(reqid):
    #         dot.node(reqid)
    #     if pd.notna(req):
    #         if req not in dot.body:
    #             dot.node(req)
    #         dot.edge(reqid, req, label="has name")

    #     if pd.notna(verified):
    #         if verified not in dot.body:
    #             dot.node(verified)
    #         dot.edge(req, verified, label="verified by")
        
    #     if pd.notna(satisfied):
    #         if satisfied not in dot.body:
    #             dot.node(satisfied)
    #         dot.edge(req, satisfied, label="satisfied by")
        # if pd.notna(result):
        #     if result not in dot.body:
        #         dot.node(result)
        #     dot.edge(verified, result, label="analysis output")
        
        # if pd.notna(result) and pd.notna(status):
        #     if status not in dot.body:
        #         dot.node(status, shape="box")
        #     dot.edge(result, status, label="verification status")
            
    # cols = st.columns([0.23 ,0.5])
    # cols[0].graphviz_chart(dot, True)

    # cols[-1].dataframe(target_req.rename({0: "values", 1: "values", 2: "values", 3: "values", 4: "values"}).T.reset_index(). \
    #     style.applymap(lambda x: 'color: black'), use_container_width=True, hide_index=True)

   