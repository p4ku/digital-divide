import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from pandas import DataFrame

# set up page details
st.set_page_config(
    page_title="Digital Divide, Digital Skills by European Country",
    page_icon="🐝",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_data
def get_data():
    users = pd.read_csv('digital_skills.csv')
    return users


@st.cache_data
def get_geometries(users: DataFrame):
    url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
    gdf_ne = gpd.read_file(url)  # zipped shapefile
    gdf_ne = gdf_ne[["NAME", "CONTINENT", "POP_EST", 'geometry']]
    df = gdf_ne

    df.info()
    #  ['Country or Area', 'Internet Users', 'Population', 'Rank', 'Percentage', 'Rank.1']

    df1 = df[['NAME', 'geometry']]
    df1.rename(columns={'NAME': 'country'}, inplace=True)

    users_2 = users.copy()

    merged = df1.merge(users2, how='left', on='country')

    return merged


df = get_data()
geo_df = get_geometries(df)

tab1, tab2 = st.tabs(
    ['**Map**', '**Data**'])

with tab1:
    st.header('Map')
    st.write(
        f'This plot shows the prevalence of basic digital skills across the UK and European Union since 2016.')

    fig = px.choropleth(geo_df,
                        locations='country',
                        locationmode='country names',
                        color="At least basic digital skills",
                        hover_name="country",
                        # color_continuous_scale=px.colors.sequential.Plasma,
                        labels={'At least basic digital skills': 'At least basic digital skills'}
                        )
    fig.update_geos(fitbounds='locations', visible=False)
    fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

with tab2:
    st.header('Data')
    st.write(f'In this table, it is possible to observe raw data.')
    columns_to_display = [col for col in df.columns if col != 'geometry']
    st.dataframe(df[columns_to_display], use_container_width=True)
