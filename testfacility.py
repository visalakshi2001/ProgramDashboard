import streamlit as st
import pandas as pd


def testfacility():

    facility = pd.read_csv("reports/TestFacilities.csv")

    cols = st.columns(2)

    with cols[0]:
        uafacilitydf = facility[facility["Test Facility"] == "UA_TestFacility"]

        st.subheader("🏭 UA Test Facility", divider="orange")

        populate_facility_details(uafacilitydf)

    with cols[1]:
        vtfacilitydf = facility[facility["Test Facility"] == "VT_TestFacility"]

        st.subheader("🏭 VT Test Facility", divider="orange")

        populate_facility_details(vtfacilitydf)

def populate_facility_details(df):

    # get the facility temperature details
    tempdf = df[["Test Facility Temp", "Test Facility Temp Value", "Test Facility Temp Unit"]].drop_duplicates().reset_index(drop=True)

    actualtemp = tempdf.iloc[0]["Test Facility Temp Value"]
    mintemp = tempdf.iloc[1]["Test Facility Temp Value"]
    maxtemp = tempdf.iloc[2]["Test Facility Temp Value"]
    tempunit = tempdf['Test Facility Temp Unit'][0]

    st.markdown("##### Available Test Conditions")
    subcols = st.columns(2)
    # subcols[0].metric(label="Actual Temperature", value=f"{actualtemp} {tempunit}", delta_color="inverse")
    subcols[0].metric(label="Minimum Temperature", value=f"{mintemp} {tempunit}", delta_color="inverse")
    subcols[1].metric(label="Maximum Temperature", value=f"{maxtemp} {tempunit}", delta_color="inverse")


    st.markdown("##### Available Researchers")
    researcher = df["Role"].value_counts().index
    st.metric(label=f"Role:", value=researcher[0])

    st.markdown("##### Available Equipments")
    vtequipment = df["Equipment"].value_counts().index
    st.dataframe(vtequipment, hide_index=True, use_container_width=True)

    # exp = st.expander("View Facility Details", icon="🏢")
    # exp.dataframe(df, hide_index=True, use_container_width=True)
    

