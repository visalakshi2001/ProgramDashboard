import streamlit as st
import pandas as pd
import re
import os

def issues_view():
    # cont = st.container(border=True)
    st.markdown("<h4>Warnings/Issues</h4>", True)
    issuesinfo("test_strategy")
    issuesinfo("test_results")
    issuesinfo("requirements")

def issuesinfo(curr_tab=""):

    cont = st.container(border=True)

    
    issues_dict = create_issues()

    if curr_tab == "test_strategy":
        issues_dict = issues_dict["test_strategy"]
        if issues_dict == []:
            cont.success("All test cases are scheduled without any clashing resourse allocation", icon="✅")
        for issue in issues_dict:
            if issue["type"] == "warning":
                cont.warning(issue["message"], icon="⚠️")
            if issue["type"] == "error":
                cont.error(issue["message"], icon="❗")
    
    if curr_tab == "requirements":
        issues_dict = issues_dict["requirements"]

        if issues_dict == []:
            cont.success("All Test Cases take place in a Facility with suitable temperature requirements", icon="✅")
        
        for issue in issues_dict:
            if issue["type"] == "warning":
                cont.warning(issue["message"], icon="⚠️")
            if issue["type"] == "error":
                cont.error(issue["message"], icon="❗")
    
    if curr_tab == "test_results":
        issues_dict = issues_dict["test_results"]

        if issues_dict == []:
            cont.success("All Test Cases are suitable for the actual temperature requirements", icon="✅")
        
        for issue in issues_dict:
            if issue["type"] == "warning":
                cont.warning(issue["message"], icon="⚠️")
            if issue["type"] == "error":
                cont.error(issue["message"], icon="❗")
        


def create_issues():
    strategy = pd.read_csv("reports/TestStrategy.csv")

    strategy_cols = strategy.columns.to_series()

    strategy_cols = strategy_cols.apply(lambda y: re.sub("\s{2,}", " ", y))
    strategy_cols = strategy_cols.apply(lambda y: ''.join(map(lambda x: x if x.islower() else " "+x, y)).strip())

    strategy_cols = strategy_cols.apply(lambda y: re.sub("Org$", "Organization", y))
    strategy_cols = strategy_cols.apply(lambda y: re.sub("\s{2,}", " ", y))

    strategy.columns = strategy_cols

    issues_dict = {}
    issues_dict["test_strategy"] = []
    issues_dict["requirements"] = []
    issues_dict["test_results"] = []

    strategy["Duration Value"] = pd.to_numeric(strategy["Duration Value"], errors='coerce')
    test_case_durations = strategy.groupby("Test Case")["Duration Value"].max()
    total_test_case_duration = test_case_durations.sum()

    sorted_tests = strategy["Test Case"].tolist()
    facilities = strategy["Facility"].tolist()
    
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

    # Calculate final test duration
    testDuration = total_test_case_duration + location_change_count * 6

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
    requirement_columns = requirements.columns.to_series()

    requirement_columns = requirement_columns.apply(lambda y: re.sub("\s{2,}", " ", y))
    requirement_columns = requirement_columns.apply(lambda y: ''.join(map(lambda x: x if x.islower() else " "+x, y)).strip())

    requirement_columns = requirement_columns.apply(lambda y: re.sub("\s{2,}", " ", y))
    requirement_columns = requirement_columns.apply(lambda y: re.sub("(Req)\s", "Requirement ", y))

    requirements.columns = requirement_columns

    test_case_temp_requirement = {}

    testcase_testfacility = strategy[["Test Case", "Facility"]].drop_duplicates().reset_index(drop=True)

    for i,row in requirements.iterrows():
        req = row["Requirement Name"]
        desc = row["Requirement Description"]
        testcase = row["Verified By"]
        testcasefacility= None

        if not "temperature" in req.lower():
            continue

        testcasefacility = testcase_testfacility[testcase_testfacility["Test Case"]==testcase]["Facility"].iloc[0]

        min_req_temp, max_req_temp = None, None

        # system shall operatre in a low-temp of at most XXdegF temperature
        # this min(low temp) >= facility_min_temp
        match_min = re.search(r'at\s+most\s+(\-?\d+)\s*deg', desc, flags=re.IGNORECASE)
        if match_min:
            min_req_temp = float(match_min.group(1))
        
        # system shall operatre in a high-temp of at least XXdegF temperature
        # this max(high temp) <= facility_max_temp
        match_max = re.search(r'at\s+least\s+(\-?\d+)\s*deg', desc, flags=re.IGNORECASE)
        if match_max:
            max_req_temp = float(match_max.group(1))
        
        test_case_temp_requirement[testcase] = {"max_req_temp": max_req_temp, 
                                                "min_req_temp": min_req_temp, 
                                                "alloted_facility": testcasefacility
                                                }
        

    facility = pd.read_csv("reports/TestFacilities.csv")
    facility_cols = facility.columns.to_series()

    facility.columns = facility_cols.apply(lambda y: ''.join(map(lambda x: x if x.islower() else " "+x, y)).strip())

    test_facility_temp_availability = {}

    facility_temp_df = facility.drop(columns=["Equipment"]).drop_duplicates().reset_index(drop=True)
    facility_temp_df["Test Facility Temp"] = facility_temp_df["Test Facility Temp"].apply(lambda x: "Min_Temp" if re.findall("(Min.*Temp)", x) != [] else x)
    facility_temp_df["Test Facility Temp"] = facility_temp_df["Test Facility Temp"].apply(lambda x: "Max_Temp" if re.findall("(Max.*Temp)", x) != [] else x)
    facility_temp_df["Test Facility Temp"] = facility_temp_df["Test Facility Temp"].apply(lambda x: "Actual_Temp" if re.findall("(Actual.*Temp)", x) != [] else x)

    facility_temp_df = facility_temp_df.drop_duplicates().reset_index(drop=True)
    
    all_facilities = facility_temp_df["Test Facility"].unique().tolist()
    
    for fac in all_facilities:
        temp_df = facility_temp_df[facility_temp_df["Test Facility"] == fac]


        mintemp = temp_df[temp_df["Test Facility Temp"] == "Min_Temp"]
        mintemp = mintemp.iloc[0]["Test Facility Temp Value"] if len(mintemp) > 0 else None

        maxtemp = temp_df[temp_df["Test Facility Temp"] == "Max_Temp"]
        maxtemp = maxtemp.iloc[0]["Test Facility Temp Value"] if len(maxtemp) > 0 else None

        actualtemp = temp_df[temp_df["Test Facility Temp"] == "Actual_Temp"]
        actualtemp = actualtemp.iloc[0]["Test Facility Temp Value"] if len(actualtemp) > 0 else None
        
        test_facility_temp_availability[fac] = {"mintemp": mintemp, "maxtemp": maxtemp, "actualtemp": actualtemp}
    
    for testcase in test_case_temp_requirement.keys():
        testcasefacility = test_case_temp_requirement[testcase]["alloted_facility"]

        facility_min_temp = test_facility_temp_availability[testcasefacility]["mintemp"]
        facility_max_temp = test_facility_temp_availability[testcasefacility]["maxtemp"]

        min_req_temp = test_case_temp_requirement[testcase]["min_req_temp"]
        max_req_temp = test_case_temp_requirement[testcase]["max_req_temp"]
        
        if min_req_temp is not None:
            if not (facility_min_temp <= min_req_temp and min_req_temp <= facility_max_temp):
                issues_dict["requirements"].append({'type': "error",
                                                'message': f"The Test Case {testcase} requires low-temp of at most {min_req_temp}degF but it takes place at Facility {testcasefacility} which does not meet the temperature requirements"}
                )
        # else:
        #     issues_dict["requirements"].append({'type': "warning",
        #                                         'message': f"Could not extract Minimum Facility Temperature value for {fac}. Value missing or incorrectly represented"}
        #         )
        
        if max_req_temp is not None:
            if not (facility_min_temp <= max_req_temp and max_req_temp <= facility_max_temp):
                issues_dict["requirements"].append({'type': "error",
                                                'message': f"The Test Case {testcase} requires high-temp of at least {max_req_temp}degF but it takes place at Facility {testcasefacility} which does not meet the temperature requirements"}
                )
        # else:
        #     issues_dict["requirements"].append({'type': "warning",
        #                                         'message': f"Could not extract Maximum Facility Temperature value for {fac}. Value missing or incorrectly represented"}
        #         )
    
    # create issues for requirements tab
    if os.path.exists("reports/TestResults.csv"):
        testresults = pd.read_csv("reports/TestResults.csv")
        results_cols = testresults.columns.to_series()

        results_cols = results_cols.apply(lambda y: ''.join(map(lambda x: x if x.islower() else " "+x, y)).strip())

        testresults.columns = results_cols.apply(lambda y: y.replace("Org", "Organization"))

        testresults_actual_temp = {}

        for i,row in testresults.iterrows():
            testcase = row["Test Case"]
            testresultstr = row["Test Result"]
            testresultval = row["Test Result Value"]

            if "Actual" in testresultstr and "Temp" in testresultstr:
                testresults_actual_temp[testcase] = {"testresult_actual_temp": testresultval}
        
        for testcase in testresults_actual_temp.keys():
            testcasefacility = test_case_temp_requirement[testcase]["alloted_facility"]

            facility_min_temp = test_facility_temp_availability[testcasefacility]["mintemp"]
            facility_max_temp = test_facility_temp_availability[testcasefacility]["maxtemp"]

            actualtemp = testresults_actual_temp[testcase]["testresult_actual_temp"]

            if actualtemp is not None:
                if not (facility_min_temp <= actualtemp and actualtemp <= facility_max_temp):
                    issues_dict["requirements"].append({'type': "error",
                                                    'message': f"The Test Case {testcase} with actual temperature value {actualtemp}degF takes place at Facility {testcasefacility} which does not meet the temperature requirements"}
                    )
            else:
                issues_dict["requirements"].append({'type': "warning",
                                                    'message': f"Could not extract Actual Temperature value for {testcase}. Value missing or incorrectly represented"}
                    )

    issues_dict["test_strategy"] = pd.DataFrame(issues_dict["test_strategy"]).drop_duplicates().to_dict('records')
    issues_dict["requirements"] = pd.DataFrame(issues_dict["requirements"]).drop_duplicates().to_dict('records')
    issues_dict["test_results"] = pd.DataFrame(issues_dict["test_results"]).drop_duplicates().to_dict('records')
    

    return issues_dict

    


# whether a rover can do a test in VT and in a given temperature condition (through python)
# can the test facility satisfy the temperature mentioned in the requirement?
# did the actual recorded temperature of the test results, fall within the expected temperature range
# Can we extract the entities from a given requirement sentence to extract things like temperature/pressure?