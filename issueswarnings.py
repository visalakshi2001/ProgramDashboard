import streamlit as st
import pandas as pd


def issues_view():
    issuesinfo()

def issuesinfo(curr_tab=""):

    cont = st.container(border=True)

    cont.markdown("<h4>Warnings/Issues</h4>", True)


    issues_dict = create_issues()

    if curr_tab == "test_strategy":
        issues_dict = issues_dict["test_strategy"]

        for issue in issues_dict:
            if issue["type"] == "warning":
                cont.warning(issue["message"], icon="⚠️")
            if issue["type"] == "error":
                cont.error(issue["message"], icon="❗")
    
    if curr_tab == "requirements":
        issues_dict = issues_dict["requirements"]

        cont.success("All Test Cases are suitable for the temperature requirements", icon="✅")
    
    if curr_tab == "test_results":
        issues_dict = issues_dict["test_results"]

        cont.success("All Test Cases take place in a Facility with suitable temperature requirements", icon="✅")


def create_issues():
    strategy = pd.read_csv("reports/TestStrategy.csv")
    issues_dict = {}
    issues_dict["test_strategy"] = []
    issues_dict["requirements"] = []
    issues_dict["test_results"] = []

    strategy["Duration Value"] = pd.to_numeric(strategy["Duration Value"], errors='coerce')
    test_case_durations = strategy.groupby("Test Case")["Duration Value"].max()
    total_test_case_duration = test_case_durations.sum()

    # Identify location changes and add 6 days per change
    df_unique = strategy.drop_duplicates(subset=["Test Case"])[["Test Case", "Facility", "Organization", "Occurs Before"]]

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
        if pd.isna(location):
            location = df_unique[df_unique["Test Case"] == test_case]["Facility"].values[0]
        if previous_location and location != previous_location and not pd.isna(location):
            location_change_count += 1
        previous_location = location

    # Add 6 days per location change
    total_travel_duration = location_change_count * 6

    # Calculate final test duration
    testDuration = total_test_case_duration + total_travel_duration

    if testDuration > 60:
        issues_dict["test_strategy"].append({"type": "warning", "message": "The test duration is more than 60 days"})
    

    test_case_researcher_df = strategy[["Test Case", "Researcher", "Facility", "Test Equipment"]]
    test_case_researcher_df = test_case_researcher_df.drop_duplicates()

    for i,row in test_case_researcher_df.iterrows():
        testcase = row["Test Case"]
        researcher = row["Researcher"]
        facility = row["Facility"]
        equipment = row["Test Equipment"]


        researcher_loc = researcher.split("_")[0]
        facility_loc = facility.split("_")[0]
        equipment_loc = equipment.split("_")[0]

        if facility_loc not in researcher_loc or researcher_loc != facility_loc or researcher_loc not in facility_loc:
            issues_dict["test_strategy"].append({'type': "error", 
                              'message': f"The Researcher {researcher} for Test Case {testcase} is not available at the assigned facility {facility}"} 
            )

        
        if facility_loc not in equipment_loc:
            issues_dict["test_strategy"].append({'type': "error",
                                             'message': f"The Equipment {equipment} for Test Case {testcase} is not available at the assigned facility {facility}"}
            )

    
    # create issues for requirements tab
    requirements = pd.read_csv("reports/Requirements.csv")
    facility = pd.read_csv("reports/TestFacilities.csv")

    for i,row in requirements.iterrows():
        req = row["ReqName"]
        desc = row["ReqDescription"]

        if not "temperature" in req.lower():
            continue
        



    issues_dict["test_strategy"] = pd.DataFrame(issues_dict["test_strategy"]).drop_duplicates().to_dict('records')
    issues_dict["requirements"] = pd.DataFrame(issues_dict["requirements"]).drop_duplicates().to_dict('records')
    issues_dict["test_results"] = pd.DataFrame(issues_dict["test_results"]).drop_duplicates().to_dict('records')
    

    return issues_dict

    


# whether a rover can do a test in VT and in a given temperature condition (through python)
# can the test facility satisfy the temperature mentioned in the requirement?
# did the actual recorded temperature of the test results, fall within the expected temperature range
# Can we extract the entities from a given requirement sentence to extract things like temperature/pressure?