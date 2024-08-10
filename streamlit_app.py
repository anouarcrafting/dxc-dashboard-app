import streamlit as st
import plotly.express as px
from helper import date_to_datetime,count_contacts_per_country,excel_pipeline, filter_satisfaction, satisfaction, successful_calls, sum_presents
import pandas as pd
st.set_page_config(layout="wide",)
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load and apply the CSS file at the start of your app
load_css('style.css')



with st.sidebar:
    file=st.file_uploader(label='load an excel file')
    if file is not None:
        dataframe = pd.ExcelFile(file)
        excel_pipeline(dataframe)
if file is not None:
    
    #st.write(dataframe)
    data=pd.read_csv("clean_data.csv")
    contact_country=count_contacts_per_country(data)
    fig1=px.bar(contact_country,x="pays", y="contact"
                ,color_discrete_sequence=["#9B86BD"])
    
    fig3=px.choropleth(data_frame=contact_country,locations="iso_alpha", color="contact", hover_name="pays", range_color=[1,20],color_continuous_scale=px.colors.sequential.Plasma)
    relance_table=data[data["status"]==0]["contact"]
    st.title('DXC dashboard')

    col1,col2=st.columns(2)
    with col1:
        
        st.markdown("<p style='font-size:20px'>Nombre de contacts par pays</p>",unsafe_allow_html=True)
        st.write(fig1)
    with col2:
        st.markdown("<p style='font-size:20px'>historique de contacts par pays</p>",unsafe_allow_html=True)
        country=st.selectbox("choose a country for filter",options=["all"]+list(contact_country["pays"]))
        history=date_to_datetime(data,country=country)
        fig2=px.line(x=history.index,y=history["contact"],color_discrete_sequence=["#9B86BD"],markers=True)
        fig2.update_layout(
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                            label="1m",
                            step="month",
                            stepmode="backward"),
                        dict(count=6,
                            label="6m",
                            step="month",
                            stepmode="backward"),
                        dict(count=1,
                            label="YTD",
                            step="year",
                            stepmode="todate"),
                        dict(count=1,
                            label="1y",
                            step="year",
                            stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(
                    visible=True
                ),
                type="date"
            )
        )
        st.write(fig2)

    col5,col6=st.columns(2)
    with col5:
        successful=successful_calls(data,country=country)
        st.markdown("<p style='text-align: center; font-size:20px'>Nombre de appels ayant succes</p>",unsafe_allow_html=True)
        st.markdown('<p class="calls_value">'+str(successful)+'</p>',unsafe_allow_html=True)
    with col6:
        calls=sum_presents(data,country=country)
        st.markdown("<p style='font-size:20px'>Nombre de pesonnes presents dans les appels</p>",unsafe_allow_html=True)
        st.markdown('<p class="calls_value">'+str(calls)+'</p>',unsafe_allow_html=True)
    col3,col4=st.columns([0.3,0.7])
    with col3:
        st.markdown("<p style='font-size:20px'>L'id des clients necessitant une relance</p>",unsafe_allow_html=True)
        st.dataframe(relance_table,hide_index=True,use_container_width=True)
    with col4:
        st.markdown("<p style='font-size:20px'>Disposition des clients</p>",unsafe_allow_html=True)
        st.write(fig3)
    # adding satisfaction table
    st.markdown("<p style='font-size:20px'>satisfaction des clients</p>",unsafe_allow_html=True)
    details=st.checkbox('show details:')
    satisfied=st.radio('filter on:',['all','satisfied','unsatisfied'])
    satisfaction_table=satisfaction(data)
    filtered_satisfaction=filter_satisfaction(satisfaction_table,details=details,satisfied=satisfied)
    st.dataframe(filtered_satisfaction,hide_index=True,use_container_width=True)
else:
    st.title('DXC dashboard')
    st.write("Please upload an excel file to get your dashboard")