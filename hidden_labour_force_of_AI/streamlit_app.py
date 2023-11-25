import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import matplotlib.cm as cm
import matplotlib.colors as colors
import plotly.express as px

# set up page details
st.set_page_config(
    page_title="Digital Divide, Hidden Labour Force of AI",
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

    gig_work = pd.read_csv('worker_country_occupation_share_2022_to_2023.csv')
    geo_gigwork = gig_work.merge(country_mapping, left_on='country', right_on='geoName')
    geo_gigwork = country_shapes.merge(geo_gigwork, left_on='code', right_on='code', how='left')

    geo_gigwork = geo_gigwork[geo_gigwork['CNTRY_NAME'] != 'Antarctica']
    cities = gpd.read_file(gpd.datasets.get_path('naturalearth_cities'))

    gigwork_cities = pd.read_json('company_mapping.json', orient='records', encoding='utf-8')

    geogigwork_cities = gpd.GeoDataFrame(gigwork_cities.merge(cities, left_on='city', right_on='name'))

    return geo_gigwork, geogigwork_cities


geo_gigwork, geogigwork_cities = get_data()

tab1, tab2, tab3 = st.tabs(
    ['**Map**', '**Map - static**', '**Data**'])

with tab1:
    st.header('Map')
    st.write(
        f'In this plot, it is possible to observe the presence of outliers. The ages **around and over 100** are most likely erroneous data inputs. These errors may have been made by accident or on purpose. For instance, some users may not want to disclose their personal information.')

    annotations = []
    # TODO: Fix annotations
    # for x, y, label, offset in zip(geogigwork_cities.geometry.centroid.x,
    #                                geogigwork_cities.geometry.centroid.y,
    #                                geogigwork_cities.company,
    #                                geogigwork_cities.offset):
    #     annotations.append(dict(
    #         text=label, x=x, y=y,
    #         showarrow=True,
    #         font=dict(color='black', size=10),
    #         xref='x', yref='y'))

    fig = px.choropleth(geo_gigwork,
                        locations='country',
                        locationmode='country names',
                        color="share",
                        hover_name="country",
                        # color_continuous_scale=px.colors.sequential.Plasma,
                        labels={'share': 'Share (%) of Online Data Entry Jobs'}
                        )
    fig.update_geos(fitbounds='locations', visible=False)
    fig.update_layout(
        margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
        annotations=annotations
    )

    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

with tab2:
    st.header('Map - static')
    st.write(
        f'In this plot, it is possible to observe the presence of outliers. The ages **around and over 100** are most likely erroneous data inputs. These errors may have been made by accident or on purpose. For instance, some users may not want to disclose their personal information.')

    # Hidden Labour Force of AI
    fig, ax = plt.subplots(1, 1, figsize=(30, 20))

    geo_gigwork.plot('share', cmap='Blues',
                     missing_kwds={
                         "color": "gainsboro",
                         "edgecolor": "lightgrey",
                         "hatch": "///",
                         "label": "Missing values",
                     },
                     vmin=0, vmax=1, ax=ax)

    arrowprops = dict(facecolor='black', shrink=0.05, width=.5, headwidth=2, headlength=1)

    for x, y, label, offset in zip(geogigwork_cities.geometry.x, geogigwork_cities.geometry.y,
                                   geogigwork_cities.company, geogigwork_cities.offset):
        ax.annotate(label, xy=(x, y), xytext=offset, textcoords="offset points", arrowprops=arrowprops, fontsize=8)

    ax.tick_params(axis='both', which='both', bottom=False, top=False, left=False, labelbottom=False, labelleft=False)
    ax.grid(False)
    ax.set_facecolor('w')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_title('Global Locations of Data Annotators')

    mappable = cm.ScalarMappable(norm=colors.Normalize(vmin=0, vmax=1, clip=False), cmap='Blues')
    plt.colorbar(mappable, ax=ax, orientation='vertical', location='right', shrink=.3,
                 label='Share (%) of Online Data Entry Jobs')

    st.pyplot(fig.figure)

with tab3:
    st.header('Data')
    st.write(f'In this table, it is possible to observe raw data.')
    columns_to_display = [col for col in geo_gigwork.columns if col != 'geometry']
    st.dataframe(geo_gigwork[columns_to_display], use_container_width=True)
