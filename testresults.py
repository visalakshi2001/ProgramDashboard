import streamlit as st
import pandas as pd


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

    cols = st.columns(2)

    with cols[0]:
        testcaseopt = st.selectbox("Select Test Case", options=testresultsdf["TestCase"].unique(), index=0)

        resultdf = testresultsdf[testresultsdf["TestCase"] == testcaseopt]

        teststr = """---\n"""
        for i,row in resultdf.iterrows():
            testcase = row["TestCase"]
            testresult = row["TestResult"]

            testresult = testresult.split(testcase + "_")[-1]
            testresult = "".join(testresult.split("_"))

            teststr = teststr + f"\t{testresult}\n"
        
        
        st.write(f"**Test Result in Test Case {testcaseopt}**")
        st.markdown(teststr)
            

    with cols[1]:
        st.markdown("#### Test Subject: Lego_Rover")
        subcols = st.columns(2)

        for i,row in resultdf.iterrows():
            testcase = row["TestCase"]
            testresult = row["TestResult"]
            testvalue = row["TestResultValue"]
            testunit = row["TestResultUnit"]
            testsubject = row["TestSubject"]

            testresult = testresult.split(testcase + "_")[-1]
            testresult = "".join(testresult.split("_"))

            subcols[i%2].metric(label=f"Test Case: {testcase}", value=f"{testvalue} {testunit}", delta=f"🧮 {testresult}")

            # when i reaches the length of resultdf, reset i counter
            if i == len(resultdf):
                i = 0
    
    exp = st.expander("View Test Results", icon="📊")
    exp.dataframe(testresultsdf, hide_index=True, use_container_width=True)