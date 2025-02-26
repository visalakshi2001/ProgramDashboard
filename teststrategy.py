import streamlit as st
import pandas as pd
import graphviz
import plotly.express as px

def teststrat():
    
    strategy = pd.read_csv("reports/TestStrategy.csv")


    strategy["DurationValue"] = pd.to_numeric(strategy["DurationValue"], errors='coerce')
    test_case_durations = strategy.groupby("TestCase")["DurationValue"].max()
    total_test_case_duration = test_case_durations.sum()

    # Identify location changes and add 6 days per change
    df_unique = strategy.drop_duplicates(subset=["TestCase"])[["TestCase", "Org", "OccursBefore"]]

    # Sort test cases based on order of execution
    execution_order = []
    visited = set()

    def get_execution_order(test_case):
        if test_case in visited or pd.isna(test_case):
            return
        visited.add(test_case)
        execution_order.append(test_case)
        next_cases = df_unique[df_unique["TestCase"] == test_case]["OccursBefore"].dropna().tolist()
        for next_case in next_cases:
            get_execution_order(next_case)

    # Start with the first test case
    first_test_case = df_unique.iloc[0]["TestCase"]
    get_execution_order(first_test_case)

    # Track location changes
    previous_location = None
    location_change_count = 0

    for test_case in execution_order:
        location = df_unique[df_unique["TestCase"] == test_case]["Org"].values[0]
        if previous_location and location != previous_location:
            location_change_count += 1
        previous_location = location

    # Add 6 days per location change
    total_travel_duration = location_change_count * 6

    # Calculate final test duration
    testDuration = total_test_case_duration + total_travel_duration
    cols = st.columns(2)

    cols[0].metric(label="Total Test Duration", value=testDuration, delta_color="inverse")

    cols[1].markdown("#### Warnings")
    cols[1].warning("The test duration is more than 60 days", icon="⚠️")

    ###################################
    ##########  GRAPH VIEW  ###########
    ###################################


    # write a code to create a graphviz tree of the columns in strategy table Test Strategy -> Test -> Test Case
    dot = graphviz.Digraph(comment='Hierarchy', strict=True)
    for index, row in strategy.iterrows():
        teststrat = row["TestStrategy"]
        test = row["Test"]
        testcase = row["TestCase"]

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
        
    st.graphviz_chart(dot, True)

    ###################################
    ##########  TABLE VIEW  ###########
    ###################################

    st.markdown("<h6>Test Strategy Table</h6>", True)
    st.dataframe(strategy, hide_index=True, use_container_width=True)


    ########################################
    ##########  SEQUENTIAL VIEW  ###########
    ########################################

    all_timeline_rows = []
    start_date = pd.to_datetime("2025-01-01")

    # We'll sort the tests by the order of occurs before
    sorted_tests = strategy["TestCase"].tolist()
    facilities = strategy["Facility"].tolist()

    settests = set()
    for i, test in enumerate(sorted_tests):

        if test in settests:
            continue
        else:
            settests.add(test)
        
        start = start_date + pd.Timedelta(days=i)
        finish = start_date + pd.Timedelta(days=i+6)

        facility = facilities[i]
        
        # We'll store one row per test in the final timeline
        all_timeline_rows.append({
            "Facility": facility,
            "TestCase": test,
            "Start":    start,
            "Finish":   finish
        })

    timeline_df = pd.DataFrame(all_timeline_rows)

#    display the text of Text case on top of each bar

    fig = px.timeline(
        timeline_df,
        x_start="Start",
        x_end="Finish",
        y="Facility",
        color="TestCase",
        text="TestCase",
        title="Test Strategy Sequence",
        
    )
    
    # Hide the X axis to hide the time scale
    # OPTIONAL: reverse the Y-axis so the first facility appears on top
    fig.update_xaxes(visible=False)
    fig.update_yaxes(autorange="reversed")

    st.plotly_chart(fig, use_container_width=True)
