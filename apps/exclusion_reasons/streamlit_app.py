import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from pandas import DataFrame

# set up page details
st.set_page_config(
    page_title="Digital Divide, Global Barriers to Internet Access",
    page_icon="🐝",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_data
def get_data():
    df = pd.read_csv('exclusion_reasons.csv')
    return df


@st.cache_data
def get_geometries(base_df: DataFrame):
    url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
    gdf_ne = gpd.read_file(url)  # zipped shapefile
    gdf_ne = gdf_ne[["NAME", "CONTINENT", "POP_EST", 'geometry']]
    df = gdf_ne

    df1 = df[['NAME', 'geometry']]
    df1.rename(columns={'NAME': 'country_name'}, inplace=True)

    users_2 = base_df.copy()

    merged = users_2.merge(df1, how='left', on='country_name')

    return merged


df = get_data()
#geo_df = get_geometries(df)

tab1, tab2, tab3 = st.tabs(
    ['**Internet Use**', '**Wireless 2G Access**', '**Data**'])

with tab1:
    st.header('Map')
    st.write(
        f'This plot shows the global penetration of internet usage as a percent of the population.')
    
    fig = px.choropleth(df, locations="ISO",
        color="Individuals using the Internet (% of population)",
        range_color=[0,100],
        hover_name="country_x", 
        projection="natural earth",
        color_continuous_scale = px.colors.sequential.Plasma,
        animation_frame="period", animation_group="ISO",
        )

#    fig.update_geos(fitbounds='locations', visible=False)
    fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

with tab2:
    st.header('Map')
    st.write(
        f'This plot shows the global penetration of 2G wireless internet.')
    
    fig = px.choropleth(df, locations="ISO",
        color="2G Wireless Access",
        range_color=[80,100],
        hover_name="country_x", 
        projection="natural earth",
        color_continuous_scale = px.colors.sequential.Plasma,
        animation_frame="period", animation_group="ISO",
        )

#    fig.update_geos(fitbounds='locations', visible=False)
    fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)


with tab3:
    st.header('Data')
    st.write(f'In this table, it is possible to observe raw data.')
    columns_to_display = [col for col in df.columns if col != 'geometry']
    st.dataframe(df[columns_to_display], use_container_width=True)
