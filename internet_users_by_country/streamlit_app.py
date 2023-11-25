import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from pandas import DataFrame

# set up page details
st.set_page_config(
    page_title="Digital Divide, Internet Users Around the World",
    page_icon="🐝",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_data
def get_data():
    users = pd.read_csv('../sandbox/List of Countries by number of Internet Users - Sheet1.csv')
    users = users.sort_values('Country or Area', ascending=False).drop_duplicates('Country or Area').sort_index()
    users['Population'] = users['Population'].str.replace(',', '').astype(int)
    users['Internet Users'] = users['Internet Users'].str.replace(',', '').astype(int)
    users['percent'] = users['Internet Users'] / users['Population']
    users['percent'] = users['percent'] * 100
    users.at[2, 'Country or Area'] = 'United States of America'
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
    users_2.rename(columns={'Country or Area': 'country'}, inplace=True)
    users2 = users_2[['country', 'percent']]

    merged = df1.merge(users2, how='left', on='country')

    return merged


df = get_data()
geo_df = get_geometries(df)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ['**Map**', '**Map - static**', '**Chart**', '**Chart 2**', '**Data**'])

with tab1:
    st.header('Map')
    st.write(
        f'In this plot, it is possible to observe the presence of outliers. The ages **around and over 100** are most likely erroneous data inputs. These errors may have been made by accident or on purpose. For instance, some users may not want to disclose their personal information.')

    fig = px.choropleth(geo_df,
                        locations='country',
                        locationmode='country names',
                        color="percent",
                        hover_name="country",
                        # color_continuous_scale=px.colors.sequential.Plasma,
                        labels={'percent': 'Percent of Internet Users'}
                        )
    fig.update_geos(fitbounds='locations', visible=False)
    fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

with tab2:
    st.header('Map - static')
    st.write(
        f'In this plot, it is possible to observe the presence of outliers. The ages **around and over 100** are most likely erroneous data inputs. These errors may have been made by accident or on purpose. For instance, some users may not want to disclose their personal information.')

    # Creating a map Percentage of Internet Users Around the World
    title = str(np.around(geo_df['percent'].mean(), decimals=2)) + '% population of the World has access to Internet'

    fig = geo_df.dropna().plot(column='percent', cmap='YlOrBr', figsize=(30, 30),
                               scheme='User_Defined',
                               classification_kwds=dict(bins=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100]),
                               edgecolor='black', legend=True)
    fig.get_legend().set_bbox_to_anchor((0.15, 0.4))
    fig.get_legend().set_title('Percentage (%)')
    fig.set_title("Percentage of Internet Users Around the World", size=30, pad=20)
    fig.axis('off')
    fig.text(-15, -60, title, horizontalalignment='left', size=15, color='black', weight='semibold')
    st.pyplot(fig.figure)

with tab3:
    st.header('Chart')
    st.write(
        f'In this plot, it is possible to observe the presence of outliers. The ages **around and over 100** are most likely erroneous data inputs. These errors may have been made by accident or on purpose. For instance, some users may not want to disclose their personal information.')

    custom_template = {'layout':
        go.Layout(
            font={'family': 'Helvetica',
                  'size': 14,
                  'color': '#1f1f1f'},

            title={'font': {'family': 'Helvetica',
                            'size': 20,
                            'color': '#1f1f1f'}},

            legend={'font': {'family': 'Helvetica',
                             'size': 14,
                             'color': '#1f1f1f'}},

            plot_bgcolor='#f2f2f2',
            paper_bgcolor='#ffffff'
        )}

    # Plotting the top 10 countries for 'Internet Users'
    df_top = df[:10]

    fig_lmr = px.bar(df_top,
                     x=df_top['Country or Area'],
                     y=df_top['Internet Users'],
                     title="<b>Top 10 Most countries with Percentage of Internet Users</b>",
                     color_discrete_sequence=['#FF7F50'])

    fig_lmr.update_layout(height=600, width=1000, template=custom_template, xaxis_title='<b>Country</b>',
                          yaxis_title='<b>Internet Users</b>')

    fig_lmr.update_yaxes(automargin=True, title_standoff=10)

    st.plotly_chart(fig_lmr)

with tab4:
    st.header('Chart 2')
    st.write(
        f'In this plot, it is possible to observe the presence of outliers. The ages **around and over 100** are most likely erroneous data inputs. These errors may have been made by accident or on purpose. For instance, some users may not want to disclose their personal information.')

    geo_df_limit_25 = geo_df.copy()[:25]
    fig = px.treemap(geo_df_limit_25,
                     path=["country"],
                     values="percent",
                     height=700,
                     width=800,
                     title='Top 25 Most countries with Percentage of Internet Users',
                     color_discrete_sequence=px.colors.qualitative.Prism)
    fig.data[0].textinfo = 'label+text+value'
    st.plotly_chart(fig)

with tab5:
    st.header('Data')
    st.write(f'In this table, it is possible to observe raw data.')
    columns_to_display = [col for col in df.columns if col != 'geometry']
    st.dataframe(df[columns_to_display], use_container_width=True)
