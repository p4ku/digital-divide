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
    df1.rename(columns={'NAME': 'country_name'}, inplace=True)

    users_2 = users.copy()

    merged = users_2.merge(df1, how='left', on='country_name')

    merged["At least basic digital skills"].fillna(-1,inplace=True)
    merged["StringencyIndex_Average"].fillna(-1,inplace=True)

    return merged

@st.cache_data
def reg_data(df:DataFrame):
    offset_df = df[['period','At least basic digital skills','ISO']]
    offset_df['offset_period'] = offset_df['period'] - 4
    offset_df = offset_df.merge(offset_df, left_on=['period','ISO'], right_on=['offset_period','ISO'],how='left',suffixes=('',' (offset)'))
    offset_df['change in basic digital skills'] = offset_df['At least basic digital skills (offset)'] - offset_df['At least basic digital skills']
    offset_df = offset_df[offset_df['period'] == 2019].sort_values('ISO')

    grouped_df = pd.DataFrame(df.groupby('ISO')['StringencyIndex_Average'].mean())

    out_df = grouped_df.merge(offset_df, left_on=['ISO'],right_on=['ISO'])
    out_df = out_df[['ISO','StringencyIndex_Average','change in basic digital skills']]
    out_df.columns = ['ISO', 'Average Lockdown Stringency', 'Change in Basic Digital Skills']

    return out_df

@st.cache_data
def generateColorScale(colors, naColor):
    colorArray=[]
    colorArray.append([0,naColor])
    for grenze, color in zip(np.linspace(0.01,1,len(colors)), colors):
        colorArray.append([grenze, color])
    return colorArray

df = get_data()
geo_df = get_geometries(df)
reg_df = reg_data(df)

tab1, tab2, tab3, tab4 = st.tabs(
    ['**Digital Skills**','**Lockdowns**', '**Regression**', '**Data**'])

with tab1:
    st.header('Digital Skills in Europe')
    st.write(
        f'This plot shows the prevalence of basic digital skills across the UK and European Union since 2016.')

    fig = px.choropleth(geo_df,
                        locations='country_name',
                        locationmode='country names',
                        color="At least basic digital skills",
                        hover_name="country_name",
                        animation_frame="period", animation_group="country",
                        color_continuous_scale=generateColorScale(colors=["white","blue"], naColor="gray"),
                        range_color=(0, np.max(geo_df["At least basic digital skills"])),
                        labels={'At least basic digital skills': 'At least basic digital skills'},
                        scope='europe'
                        )
    fig.update_geos(fitbounds='locations', visible=False)
    fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

with tab2:
    st.header('COVID-19 Lockdown Intensity')
    st.write(
        f'This plot shows the intensity of government lockdowns during the COVID-19 pandemic.')

    fig = px.choropleth(geo_df,
                        locations='country_name',
                        locationmode='country names',
                        color="StringencyIndex_Average",
                        hover_name="country_name",
                        animation_frame="period", animation_group="country",
                        color_continuous_scale=generateColorScale(colors=["white","blue"], naColor="gray"),
                        range_color=(0, np.max(geo_df["StringencyIndex_Average"])),
                        labels={'StringencyIndex_Average': 'Lockdown Stringency'},
                        scope='europe'
                        )
    fig.update_geos(fitbounds='locations', visible=False)
    fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

with tab3:

    st.header('Regression')
    st.write('This plot compares the intensity of government lockdowns to the change in digital skills over the same period.')

    fig = px.scatter(reg_df, y='Change in Basic Digital Skills',
                     x='Average Lockdown Stringency',
                     trendline='ols',trendline_color_override='grey',
                     hover_name='ISO')
    fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

with tab4:
    st.header('Data')
    st.write(f'In this table, it is possible to observe raw data.')
    columns_to_display = [col for col in geo_df.columns if col != 'geometry']
    st.dataframe(geo_df[columns_to_display], use_container_width=True)
