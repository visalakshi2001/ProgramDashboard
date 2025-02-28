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
    graphchoice = st.selectbox("Select view", ["System Architecture", "Mission Architecture"], index=0)

    # initiate a empty diagraph
    dot = graphviz.Digraph(comment='Hierarchy', strict=True)

    cols = st.columns(2)
    
    if graphchoice == "System Architecture":
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
                    dot.node(comp,)
                if pd.notna(subsys):
                    dot.edge(subsys, comp, label="has subject")  
        cols[0].graphviz_chart(dot, True)
    
    elif graphchoice == "Mission Architecture":
        for index, row in  mission.iterrows():
            mission = row["Mission"]
            env = row["Env"]
            missent = row["MissionEntities"]

            dot.node(mission)

            if pd.notna(env):
                if env not in dot.body:
                    dot.node(env)
                dot.edge(mission, env, label="has environment")
            if pd.notna(missent):
                dot.node(missent)
                # dot.edge(missname, misscomp, arrowhead="diamond", label="has component")
                dot.edge(env, missent, label="has entity")

        cols[0].graphviz_chart(dot, True)
    




