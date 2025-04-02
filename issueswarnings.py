import streamlit as st
import pandas as pd


def issuesinfo():

    cont = st.container(border=True)

    cont.markdown("<h4>Warnings/Issues</h4>", True)


    cont.warning("The test duration is more than 60 days", icon="⚠️")

    cont.error("The Equipment VT_Stopwatch for Test Case T2_1 is not available at the assigned facility UA_TestFacility", icon="❗")
    cont.error("The Researcher UA_Researcher for Test Case T3_3 is not available at the assigned facility VT_TestFacility", icon="❗")

    # create_issues()


def create_issues():
    strategy = pd.read_csv("reports/TestStrategy.csv")
    issues_dict = {}

    strategy["Duration Value"] = pd.to_numeric(strategy["Duration Value"], errors='coerce')
    test_case_durations = strategy.groupby("Test Case")["Duration Value"].max()
    total_test_case_duration = test_case_durations.sum()

    # Identify location changes and add 6 days per change
    df_unique = strategy.drop_duplicates(subset=["Test Case"])[["Test Case", "Organization", "Occurs Before"]]

    # Sort test cases based on order of execution
    execution_order = []
    visited = set()

    def get_execution_order(test_case):
        if test_case in visited or pd.isna(test_case):
            return
        visited.add(test_case)
        execution_order.append(test_case)
        next_cases = df_unique[df_unique["Test Case"] == test_case]["Occurs Before"].dropna().tolist()
        for next_case in next_cases:
            get_execution_order(next_case)

    # Start with the first test case
    first_test_case = df_unique.iloc[0]["Test Case"]
    get_execution_order(first_test_case)

    # Track location changes
    previous_location = None
    location_change_count = 0

    for test_case in execution_order:
        location = df_unique[df_unique["Test Case"] == test_case]["Organization"].values[0]
        if previous_location and location != previous_location:
            location_change_count += 1
        previous_location = location

    # Add 6 days per location change
    total_travel_duration = location_change_count * 6

    # Calculate final test duration
    testDuration = total_test_case_duration + total_travel_duration

    if testDuration > 60:
        issues_dict["testDurationError"] = {"type": "warning", "message": "The test duration is more than 60 days"}
    


# whether a rover can do a test in VT and in a given temperature condition (through python)
# can the test facility satisfy the temperature mentioned in the requirement?
# did the actual recorded temperature of the test results, fall within the expected temperature range
# Can we extract the entities from a given requirement sentence to extract things like temperature/pressure?