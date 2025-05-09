import streamlit as st
import pandas as pd
import re

from jsontocsv import validate_csv, json_to_csv

def testfacilityvalidate():
    expected_cols = [ "TestFacility" , "TestFacilityTemp" , "TestFacilityTempMeas" , "TestFacilityTempValue" , "TestFacilityTempUnit" , "Equipment" ]
    is_valid = validate_csv("reports/TestFacilities.csv", expected_cols)
    if not is_valid:
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
    else:
        testfacility()


def testfacility():

    facility = pd.read_csv("reports/TestFacilities.csv")

    cols = st.columns(2)

    facility_cols = facility.columns.to_series()

    facility.columns = facility_cols.apply(lambda y: ''.join(map(lambda x: x if x.islower() else " "+x, y)).strip())


    with cols[0]:
        mtlemmonfacilitydf = facility[facility["Test Facility"] == "MtLemmon_TestFacility"]

        st.subheader("🏭 Mt. Lemmon Test Facility", divider="orange")

        populate_facility_details(mtlemmonfacilitydf)

    with cols[1]:
        yumafacilitydf = facility[facility["Test Facility"] == "Yuma_TestFacility"]

        st.subheader("🏭 Yuma Test Facility", divider="orange")

        populate_facility_details(yumafacilitydf)

def populate_facility_details(df):

    # get the facility temperature details
    tempdf = df[["Test Facility Temp", "Test Facility Temp Value", "Test Facility Temp Unit"]].drop_duplicates().reset_index(drop=True)


    tempdf["Test Facility Temp"] = tempdf["Test Facility Temp"].apply(lambda x: "Min_Temp" if re.findall("(Min.*Temp)", x) != [] else x)
    tempdf["Test Facility Temp"] = tempdf["Test Facility Temp"].apply(lambda x: "Max_Temp" if re.findall("(Max.*Temp)", x) != [] else x)
    tempdf["Test Facility Temp"] = tempdf["Test Facility Temp"].apply(lambda x: "Actual_Temp" if re.findall("(Actual.*Temp)", x) != [] else x)

    # actualtemp = tempdf.iloc[0]["Test Facility Temp Value"]
    mintemp = tempdf[tempdf["Test Facility Temp"] == "Min_Temp"].iloc[0]["Test Facility Temp Value"]
    maxtemp = tempdf[tempdf["Test Facility Temp"] == "Max_Temp"].iloc[0]["Test Facility Temp Value"]
    tempunit = tempdf['Test Facility Temp Unit'][0]

    st.markdown("##### Available Test Conditions")
    subcols = st.columns(2)
    # subcols[0].metric(label="Actual Temperature", value=f"{actualtemp} {tempunit}", delta_color="inverse")
    subcols[0].metric(label="Minimum Temperature", value=f"{mintemp} {tempunit}", delta_color="inverse")
    subcols[1].metric(label="Maximum Temperature", value=f"{maxtemp} {tempunit}", delta_color="inverse")


    st.markdown("##### Available Researchers")
    researcher = df.iloc[0]["Test Facility"]
    researcher = researcher.split("_")[0].split("TestFacility")[0]
    researcher = researcher + "_Researcher"
    st.markdown(f"> {researcher}", unsafe_allow_html=True)
    # researcher = df["Role"].value_counts().index
    # st.metric(label=f"Role:", value=researcher[0])

    st.markdown("##### Available Equipments")
    vtequipment = df["Equipment"].value_counts().index
    st.dataframe(vtequipment, hide_index=True, use_container_width=True)

    # exp = st.expander("View Facility Details", icon="🏢")
    # exp.dataframe(df, hide_index=True, use_container_width=True)
    

