import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import matplotlib.cm as cm
import matplotlib.colors as colors
import plotly.express as px

# set up page details
st.set_page_config(
    page_title="Digital Divide, Study Location",
    page_icon="🐝",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_data
def get_data():
    country_mapping = pd.read_json('country_mapping.json', orient='records', encoding='utf-8')

    country_shapes = gpd.read_file(
        'https://services.arcgis.com/B7NI2jUD81lCgSpx/arcgis/rest/services/Assignment_6_Spatial_Reference_Systems/FeatureServer/1/query?outFields=*&where=1%3D1&f=geojson')
    country_shapes = country_shapes.merge(country_mapping, left_on='CNTRY_NAME', right_on='geoName', how='left')

    # Load data from study_location_data.csv

    df = pd.read_csv('./study_location_data.csv')
    geo_df = df.merge(country_mapping, left_on='country', right_on='geoName')
    geo_df = country_shapes.merge(geo_df, left_on='code', right_on='code', how='left')
    geo_df = geo_df[geo_df['CNTRY_NAME'] != 'Antarctica']

    geo_df.rename(columns={'country': 'country_data'}, inplace=True)
    geo_df.rename(columns={'CNTRY_NAME': 'country'}, inplace=True)

    # Add 0 for non-existing values
    geo_df['number'] = geo_df['number'].fillna(0)

    return geo_df


geo_df = get_data()

tab1, tab2, tab3 = st.tabs(
    ['**Map**', '**Map - static**', '**Data**'])

with tab1:
    st.header('Map')
    st.write('Map with the number of studies')

    annotations = []
    # Create a choropleth map, but change color to GRAY for no data
    fig = px.choropleth(geo_df,
                        locations='country',
                        locationmode='country names',
                        color="number",
                        hover_name="country",
                        labels={'number': 'Number of studies'},
                        color_continuous_scale=[
                            [0, '#FEFEFE'],  # Color for missing values
                            [0.1, 'blue'],  # Color for low values
                            [1, 'darkblue']  # Color for high values
                        ],
                        range_color=[0, geo_df['number'].max()]  # Ensure the range covers the actual data
                        )

    fig.update_geos(fitbounds='locations', visible=False)
    fig.update_layout(
        margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
        annotations=annotations
    )

    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

with tab2:
    st.header('Map - static')
    st.write('Static map with the number of studies')

    # Hidden Labour Force of AI
    fig, ax = plt.subplots(1, 1, figsize=(30, 20))

    geo_df.plot('number', cmap='Blues',
                missing_kwds={
                    "color": "gainsboro",
                    "edgecolor": "lightgrey",
                    "hatch": "///",
                    "label": "Missing values",
                },
                vmin=geo_df['number'].min(),
                vmax=geo_df['number'].max(),
                ax=ax)

    ax.tick_params(axis='both', which='both', bottom=False, top=False, left=False, labelbottom=False, labelleft=False)
    ax.grid(False)
    ax.set_facecolor('w')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_title('Study Location - Number of studies')

    mappable = cm.ScalarMappable(
        norm=colors.Normalize(vmin=geo_df['number'].min(), vmax=geo_df['number'].max(), clip=False), cmap='Blues')
    plt.colorbar(mappable, ax=ax, orientation='horizontal', location='top', shrink=.3,
                 label='Number of studies')

    st.pyplot(fig.figure)

with tab3:
    st.header('Data')
    st.write(f'In this table, it is possible to observe raw data.')
    columns_to_display = [col for col in geo_df.columns if
                          col not in ['geometry', 'geoName_y', 'geoName_x', 'OBJECTID']]
    st.dataframe(geo_df[columns_to_display], use_container_width=True)
