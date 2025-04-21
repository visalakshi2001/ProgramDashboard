import streamlit as st
import pandas as pd

from jsontocsv import validate_csv, json_to_csv
from issueswarnings import issuesinfo

def testresultsvalidate():

    expected_cols = ["TestCase", "TestSubject", "TestResult", "TestResultValue", "TestResultUnit"]
    is_valid = validate_csv("reports/TestResults.csv", expected_cols)
    if not is_valid:
        st.toast("TestResults.csv is not uploaded correctly", icon="🚨")
        st.write("Use the Edit Data button to upload TestResults.json file")
        # savefilename = filename = "TestResults.json"
        # try:
        #     conn = st.session_state["conn"]
        #     with open(f"reports/{savefilename}", "wb+") as f:
        #             response = (
        #                 conn.storage
        #                 .from_("legorover")
        #                 .download(f"reports_full/{filename}")
        #             )
        #             f.write(response)
        #     csv_op_file_name = filename.split(".json")[0].strip().translate({ord(ch): None for ch in '0123456789'}).strip() + ".csv"
        #     json_to_csv(json_input_path=f"reports/{savefilename}", csv_output_path="reports/" + csv_op_file_name)
        # except:
        #     print(f"{filename} is either missing or corrupted upload it to cloud and restart the app")
    
    else:
        testresults()


def testresults():

    st.write(
        """
        <style>
        [data-testid="stMetricDelta"] svg {
            display: none;
        }
        
        [data-testid="stMetricDelta"] > div {
            color: #b00068;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    testresultsdf = pd.read_csv("reports/TestResults.csv")

    results_cols = testresultsdf.columns.to_series()

    results_cols = results_cols.apply(lambda y: ''.join(map(lambda x: x if x.islower() else " "+x, y)).strip())

    testresultsdf.columns = results_cols.apply(lambda y: y.replace("Org", "Organization"))

    st.markdown("#### Test Subject: Lego_Rover")
    cols = st.columns(2)

    with cols[0]:
        testcaseopt = st.selectbox("Select Test Case", options=testresultsdf["Test Case"].unique(), index=0)

        resultdf = testresultsdf[testresultsdf["Test Case"] == testcaseopt]

        cont = st.container(border=True)
        subcols = cont.columns(2)
        for i,row in resultdf.iterrows():
            testcase = row["Test Case"]
            testresult = row["Test Result"]
            testvalue = row["Test Result Value"]
            testunit = row["Test Result Unit"]
            testsubject = row["Test Subject"]

            testresult = testresult.split(testcase + "_")[-1]
            testresult = "".join(testresult.split("_"))

            subcols[i%2].metric(label=f"🔭 Test Case: {testcase}", value=f"{testvalue} {testunit}", delta=f"🧮 {testresult}")

        # teststr = """---\n"""
        # for i,row in resultdf.iterrows():
        #     testcase = row["Test Case"]
        #     testresult = row["Test Result"]

        #     testresult = testresult.split(testcase + "_")[-1]
        #     testresult = "".join(testresult.split("_"))

        #     teststr = teststr + f"\t{testresult}\n"
        
        
        # st.write(f"**Test Result in Test Case {testcaseopt}**")
        # st.markdown(teststr)
            

    with cols[1]:
        attributeopt = st.selectbox("Select Test Result Attribute", 
                                    options=testresultsdf["Test Result"].apply(lambda x: "_".join(x.split("_")[2:])).unique(), 
                                    index=0, format_func=lambda x: "".join(x.split("_")))

        resultdf = testresultsdf[testresultsdf["Test Result"].str.contains(attributeopt)].reset_index(drop=True)


        cont = st.container(border=True)
        subcols = cont.columns(3)
        with cont:
            for i,row in resultdf.iterrows():
                testcase = row["Test Case"]
                testresult = row["Test Result"]
                testvalue = row["Test Result Value"]
                testunit = row["Test Result Unit"]
                testsubject = row["Test Subject"]

                testresult = testresult.split(testcase + "_")[-1]
                testresult = "".join(testresult.split("_"))
                
                subcols[i%3].metric(label=f"🧮 {testresult}", value=f"{testvalue} {testunit}", delta=f"🔭 Test Case: {testcase}")
    

    cols = st.columns([0.6, 0.4])

    with cols[0]:
        exp = st.expander("View Test Results", icon="📊")
        exp.dataframe(testresultsdf, hide_index=True, use_container_width=True)
    
    with cols[1]:
        try:
            issuesinfo(curr_tab="test_results")
        except:
            st.write("There is an internal error in displaying the test warnings")