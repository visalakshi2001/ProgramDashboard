import streamlit as st
import pandas as pd

# for making UML diagrams
import graphviz


# ########## ARCHITECTURE VIEW FUNCTION
def sysarcfunc():
    # read the data for the architecture
    system = pd.read_csv("reports/SystemArchitecture.csv")
    mission = pd.read_csv("reports/MissionArchitecture.csv")

    # Make a dropdown selection menu, with a title, and list of options. 
    # this component returns the variable that is selected
    graphchoice = st.selectbox("Select view", ["System Architechture", "Missions"], index=0)

    # initiate a empty diagraph
    dot = graphviz.Digraph(comment='Hierarchy', strict=True)
    
    if graphchoice == "System Architechture":
        # st.dataframe(system)
        for index, row in system.iterrows():
            soi = row["SOI"]
            subsys = row["Subsystem"]
            comp = row["Component"]

            if pd.notna(soi):
                dot.node(soi)

            if pd.notna(subsys):
                if subsys not in dot.body:
                    dot.node(subsys)
                if pd.notna(soi):
                    dot.edge(soi, subsys, label="has subsystem")
            
            if pd.notna(comp):
                if comp not in dot.body:
                    dot.node(comp, shape="box")
                if pd.notna(subsys):
                    dot.edge(subsys, comp, label="has component")  
        st.graphviz_chart(dot, True)
    
    elif graphchoice == "Missions":
        for index, row in  mission.iterrows():
            mission = row["Mission"]
            env = row["Env"]
            missent = row["MissionEntities"]

            dot.node(mission)

            if pd.notna(env):
                if env not in dot.body:
                    dot.node(env)
                dot.edge(mission, env, label="has mission")
            if pd.notna(missent):
                dot.node(missent, shape="box")
                # dot.edge(missname, misscomp, arrowhead="diamond", label="has component")
                dot.edge(env, missent, label="has component")

        st.graphviz_chart(dot, True)
    




