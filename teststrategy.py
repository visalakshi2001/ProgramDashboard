import streamlit as st
import pandas as pd
import numpy as np
import graphviz
import plotly.express as px
from datetime import datetime
import re
import os


from issueswarnings import issuesinfo
from jsontocsv import json_to_csv, validate_csv

def teststratvalidate():
    expected_cols_strat = [ "TestStrategy" , "Test" , "TestCase" , "TestSubject" , "TestProcedure" , "Researcher" , "ResearcherOrg" , "Facility" , "Org" , "DurationValue" , "DurationUnit" , "OccursBefore" , "TestEquipment" ]
    expected_cols_facility = [ "TestFacility" , "TestFacilityTemp" , "TestFacilityTempMeas" , "TestFacilityTempValue" , "TestFacilityTempUnit" , "Equipment" ]
    
    is_valid_strat = validate_csv("reports/TestStrategy.csv", expected_cols_strat, skip_non_null_check=True)
    is_valid_facility = validate_csv("reports/TestFacilities.csv", expected_cols_facility)

    if not is_valid_strat:
        st.toast("TestStrategy.csv is not uploaded correctly", icon="🚨")
        savefilename = filename = "TestStrategy.json"
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
    
    if not is_valid_facility:
        st.toast("TestFacilities.csv is not uploaded correctly", icon="🚨")
        savefilename = filename = "TestFacilities.json"
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
    
    if not (is_valid_facility or is_valid_strat):
        st.write("Use the edit data button to upload valid TestStrategy.json and TestFacility.json files")
    else:
        teststrat()

def teststrat():
    
    strategy = pd.read_csv("reports/TestStrategy.csv")
    facilities = pd.read_csv("reports/TestFacilities.csv")

    strategy_cols = strategy.columns.to_series()

    strategy_cols = strategy_cols.apply(lambda y: re.sub("\s{2,}", " ", y))
    strategy_cols = strategy_cols.apply(lambda y: ''.join(map(lambda x: x if x.islower() else " "+x, y)).strip())

    strategy_cols = strategy_cols.apply(lambda y: re.sub("Org$", "Organization", y))
    strategy_cols = strategy_cols.apply(lambda y: re.sub("\s{2,}", " ", y))

    strategy.columns = strategy_cols

    # strategy = strategy.sort_values(by=["Test Case"])


    # strategy.to_csv("reports/TestStrategy.csv", index=False)

    ###################################
    ##########  METRIC VIEW  ##########
    ###################################
    strategy["Duration Value"] = pd.to_numeric(strategy["Duration Value"], errors='coerce')
    test_case_durations = strategy.groupby("Test Case")["Duration Value"].max()
    total_test_case_duration = test_case_durations.sum()

    strategysubset = strategy[["Test Case", "Occurs Before", "Facility"]].drop_duplicates()
    testlink = strategysubset.dropna(subset=["Occurs Before"]).set_index("Test Case")["Occurs Before"].to_dict()
    # ── Produce the mapping facility list (not the correct order right now) ─────
    facilitylink = strategysubset.set_index('Test Case')['Facility'].to_dict()

    sorted_tests = []
    # ── Find the head of the chain (it never appears in OccursBefore) ───────────
    current_test = start = (set(testlink.keys()) - set(testlink.values())).pop()
    while True:
        sorted_tests.append(current_test)
        next_test = testlink.get(current_test)
        if not next_test:
            break
        current_test = next_test
    
    facilities = [facilitylink[testcase] for testcase in sorted_tests]
    
    previous_facility = None
    settests = set()
    location_change_count = 0
    for i, test in enumerate(sorted_tests):

        if test in settests:
            continue
        settests.add(test)

        facility = facilities[i]

        if previous_facility is not None and facility != previous_facility:
            location_change_count += 1
        
        previous_facility = facility

    # Identify location changes and add 6 days per change
    # df_unique = strategy.drop_duplicates(subset=["Test Case"])[["Test Case", "Facility", "Organization", "Occurs Before"]]

    # Sort test cases based on order of execution
    # execution_order = []
    # visited = set()

    # def get_execution_order(test_case):
    #     if test_case in visited or pd.isna(test_case):
    #         return
    #     visited.add(test_case)
    #     execution_order.append(test_case)
    #     next_cases = df_unique[df_unique["Test Case"] == test_case]["Occurs Before"].dropna().tolist()
    #     for next_case in next_cases:
    #         get_execution_order(next_case)

    # # Start with the first test case
    # first_test_case = df_unique.iloc[0]["Test Case"]
    # get_execution_order(first_test_case)

    # # Track location changes
    # previous_location = None
    # location_change_count = 0

    # # st.write(execution_order)

    # for test_case in execution_order:
    #     location = df_unique[df_unique["Test Case"] == test_case]["Organization"].values[0]
    #     if pd.isna(location):
    #         location = df_unique[df_unique["Test Case"] == test_case]["Facility"].values[0]
    #     if previous_location and location != previous_location and not pd.isna(location):
    #         location_change_count += 1
    #     previous_location = location

    # st.write(location_change_count)

    # # Add 6 days per location change
    # total_travel_duration = location_change_count * 6

    # Calculate final test duration
    testDuration = total_test_case_duration + (location_change_count * 6)

    #############################################################################################

    # calculate total test cases
    totalTestCases = strategy["Test Case"].nunique()

    #############################################################################################

    # calculate total tests
    totalTests = strategy["Test"].nunique()

    #############################################################################################

    # calculate total test facilities
    totalFacilities = strategy["Facility"].nunique()

    #############################################################################################

    # calculate total test equipment
    totalEquipment = strategy["Test Equipment"].nunique()

    #############################################################################################

    # calculate total test procedures
    totalProcedures = strategy["Test Procedure"].nunique()


    cols = st.columns([0.4, 0.7])

    with cols[0]: 
        subcols = st.columns(3)   
        subcols[0].metric(label="Total Test Duration", value=f"{int(testDuration)} days", delta_color="inverse")
        # subcols[0].metric(label="Total Test Duration", value=f"{int(52)} days", delta_color="inverse")
        subcols[1].metric(label="Total Test Cases", value=totalTestCases, delta_color="inverse")
        subcols[2].metric(label="Total Tests", value=totalTests, delta_color="inverse")
        subcols[0].metric(label="Total Test Facilities", value=totalFacilities, delta_color="inverse")
        subcols[1].metric(label="Total Test Equipment", value=totalEquipment, delta_color="inverse")
        subcols[2].metric(label="Total Test Procedures", value=totalProcedures, delta_color="inverse")


    with cols[1]:
        st.markdown("<h4>Warnings/Issues</h4>", True)
        try:
            issuesinfo(curr_tab="test_strategy")
        except:
            st.write("There is an internal error in displaying the test warnings")
    
    cols[0].write("---")
    # viewopts = ["Structure", "Table", "Sequence Timeline"]
    # viewopt = cols[0].selectbox("Select a view to explore test strategy", options=viewopts)

    ###################################
    ##########  GRAPH VIEW  ###########
    ###################################
    
    make_graph_view(strategy=strategy)

    ########################################
    ##########  SEQUENTIAL VIEW  ###########
    ########################################

    make_sequence_view(strategy=strategy, test_case_durations=test_case_durations, testDuration=testDuration)


    ###################################
    ##########  TABLE VIEW  ###########
    ###################################
    cont = st.container(border=True)
    showtable = cont.checkbox("Show Tabular Explorer")

    if showtable:
        make_table_view(strategy=strategy)    




def make_graph_view(strategy):
    cont = st.container(border=True)
    cont.markdown("<h6>Test Strategy Structure</h6>", True)

    # write a code to create a graphviz tree of the columns in strategy table Test Strategy -> Test -> Test Case
    dot = graphviz.Digraph(comment='Hierarchy', strict=True)
    for index, row in strategy.iterrows():
        teststrat = row["Test Strategy"]
        test = row["Test"]
        testcase = row["Test Case"]

        if pd.notna(teststrat):
            dot.node(teststrat)
        if pd.notna(test):
            if test not in dot.body:
                dot.node(test)
            dot.edge(teststrat, test, label="has test")
        if pd.notna(testcase):
            if testcase not in dot.body:
                dot.node(testcase, shape="box")
            dot.edge(test, testcase, label="has test case")
    
    cont.graphviz_chart(dot, True)



def make_table_view(strategy):
    st.markdown("<h6>Test Strategy Explorer</h6>", True)
    subsetstrategy = strategy.drop(columns=["Test Equipment", "Occurs Before"])
    subsetstrategy = subsetstrategy.dropna(axis=1, how="all")
    # save column order for later displaying
    column_order = subsetstrategy.columns
    subsetcols = [col for col in subsetstrategy.columns if col != "Duration Value"]
    subsetstrategy = subsetstrategy.groupby(subsetcols, as_index=False)["Duration Value"].max()
    exp = st.expander("View Entire Test Strategy Table", icon="🗃️")
    exp.dataframe(subsetstrategy[column_order], hide_index=True, use_container_width=True)

    cols = st.columns([0.1,0.9])
    with cols[0]:
        testopt = st.radio("Select Test", options=np.unique(strategy["Test"]), index=0)

        caseopts = strategy[strategy["Test"] == testopt]["Test Case"].value_counts().index.tolist() + ["All"]
        testcaseopt = st.radio("Select Test Case", options=caseopts, index=0)

    with cols[1]:
        if testcaseopt == "All":
            selectedstrategy = strategy[strategy["Test"] == testopt]
        else:
            selectedstrategy = strategy[(strategy["Test"] == testopt) & (strategy["Test Case"] == testcaseopt)]
        st.dataframe(selectedstrategy, hide_index=True, use_container_width=True, height=280)



def make_sequence_view(strategy, test_case_durations, testDuration):
    
    # if os.path.exists("reports/TestStrategyTimeline.csv"):
    #     timeline_df = pd.read_csv("reports/TestStrategyTimeline.csv")
    # else:
    all_timeline_rows = []
    # start_date = pd.to_datetime("2025-01-01")
    current_start = pd.to_datetime("2025-01-01")

    # ── Build a mapping  TestCase  →  OccursBefore ──────────────────────────────
    strategysubset = strategy[["Test Case", "Occurs Before", "Facility"]].drop_duplicates()
    testlink = strategysubset.dropna(subset=["Occurs Before"]).set_index("Test Case")["Occurs Before"].to_dict()
    # ── Produce the mapping facility list (not the correct order right now) ─────
    facilitylink = strategysubset.set_index('Test Case')['Facility'].to_dict()

    sorted_tests = []
    # ── Find the head of the chain (it never appears in OccursBefore) ───────────
    current_test = start = (set(testlink.keys()) - set(testlink.values())).pop()
    while True:
        sorted_tests.append(current_test)
        next_test = testlink.get(current_test)
        if not next_test:
            break
        current_test = next_test
    
    facilities = [facilitylink[testcase] for testcase in sorted_tests]

    previous_facility = None
    settests = set()
    duration_dict = test_case_durations.to_dict()
    for i, test in enumerate(sorted_tests):

        if test in settests:
            continue
        settests.add(test)

        facility = facilities[i]

        if previous_facility is not None and facility != previous_facility:
            transition_start  = current_start
            transition_finish = transition_start + pd.Timedelta(days=5)  # 6-day block minus 1
            # Add a row to represent the transition block
            all_timeline_rows.append({
                "Facility": "Yuma_TestFacility",          # or any label you prefer
                "Test Case": f"Transit",
                "Start":    transition_start,
                "Finish":   transition_finish
            })
            all_timeline_rows.append({
                "Facility": "MtLemmon_TestFacility",          # or any label you prefer
                "Test Case": f"Transit",
                "Start":    transition_start,
                "Finish":   transition_finish
            })
            # Now move the pointer to the next day after the transition
            current_start = transition_finish #+ pd.Timedelta(days=1)
        
        start = current_start
        timestep = duration_dict[test]
        if timestep < 1:
            # adjusting the width of the bar less than 1 day to fit the text label
            timestep = timestep + .85
        # elif timestep == 7.5:
        #     timestep = 7
        finish = start + pd.Timedelta(days=timestep)
        
        # We'll store one row per test in the final timeline
        all_timeline_rows.append({
            "Facility": facility,
            "Test Case": test,
            "Start":    start,
            "Finish":   finish
        })

        current_start = finish #+ pd.Timedelta(days=1)
        previous_facility = facility

    timeline_df = pd.DataFrame(all_timeline_rows)

    timeline_df.to_csv("reports/TestStrategyTimeline.csv", index=False)

    # display the text of Text case on top of each bar
    fig = px.timeline(
        timeline_df,
        x_start="Start",
        x_end="Finish",
        y="Facility",
        color="Test Case",
        text="Test Case",
        title="Test Strategy Sequence",
        color_discrete_sequence=px.colors.qualitative.Plotly,
        color_discrete_map={"Transit": "#e4e6eb"},
    )

    # adjust the x-axis scale
    x_end = int(6 * ((testDuration) // 6) + 8)
    # Hide the X axis to hide the time scale
    # fig.update_xaxes(visible=False)
    # Hide the legend and reduce the gap between bars
    fig.update_layout(
        bargap=0,
        showlegend=False,
        xaxis = dict(
            title_text = "Day Count",
            tickmode = "array",
            tickvals = [pd.to_datetime("2025-01-01") + pd.Timedelta(days=i) for i in range(0, x_end, 6)],
            ticktext = [f"Day {i}" for i in range(0, x_end, 6)],
            range = [pd.to_datetime("2025-01-01"), pd.to_datetime("2025-01-01") + pd.Timedelta(days=x_end)]
        )
    )
    # vlinedate = pd.to_datetime("2025-01-01") + pd.Timedelta(days=65.5)
    # displaydate = vlinedate.date()
    # fig.add_vline(x=datetime(displaydate.year, displaydate.month, displaydate.day, vlinedate.hour+1).timestamp() * 1000 + 500, annotation_text= f"Day 64")
    # OPTIONAL: reverse the Y-axis so the first facility appears on top
    fig.update_yaxes(autorange="reversed")
    
    cont = st.container(border=True)
    cont.plotly_chart(fig, use_container_width=True)