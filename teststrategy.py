import streamlit as st
import pandas as pd
import graphviz
import plotly.express as px

def teststrat():
    
    strategy = pd.read_csv("reports/TestStrategy.csv")

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

    st.markdown("<h6>Test Strategy Sequence</h6>", True)
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
        title="Test Execution Sequence by Facility",
        
    )
    

    # OPTIONAL: reverse the Y-axis so the first facility appears on top
    fig.update_yaxes(autorange="reversed")

    st.plotly_chart(fig, use_container_width=True)

    # st.dataframe(timeline_df, hide_index=True, use_container_width=True)
