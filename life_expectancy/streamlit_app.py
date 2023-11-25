import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# set up page details
st.set_page_config(
    page_title="Digital Divide, Life Expectation Around the World",
    page_icon="🐝",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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


@st.cache_data
def get_test_data():
    return px.data.gapminder()


df_test = get_test_data()

tab1, tab2, tab3, tab4 = st.tabs(
    ['**Map with slider**', '**Map with slider 2**', '**Chart with slider**', '**Time Series Data**'])

with tab1:
    st.header('Map with slider')
    st.write(
        f'In this plot, it is possible to observe the presence of outliers. The ages **around and over 100** are most likely erroneous data inputs. These errors may have been made by accident or on purpose. For instance, some users may not want to disclose their personal information.')

    fig = px.choropleth(df_test,
                        locations="iso_alpha",
                        color="lifeExp",
                        hover_name="country",
                        animation_frame="year",
                        color_continuous_scale=px.colors.sequential.Plasma
                        )

    fig.update_geos(fitbounds='locations', visible=False)
    fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    fig.update_layout(height=600, width=1000, template=custom_template,
                      xaxis_title='<b>GDP per Capita</b>',
                      yaxis_title='<b>Life Expectation</b>')
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

with tab2:
    st.header('Map with slider 2')
    st.write(
        f'In this plot, it is possible to observe the presence of outliers. The ages **around and over 100** are most likely erroneous data inputs. These errors may have been made by accident or on purpose. For instance, some users may not want to disclose their personal information.')

    df_test_2 = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2011_us_ag_exports.csv')
    data = [dict(type='choropleth',
                 locations=df_test_2['code'].astype(str),
                 z=df_test_2['total exports'].astype(float),
                 locationmode='USA-states')]

    # let's create some more additional, data
    for i in range(5):
        data.append(data[0].copy())
        data[-1]['z'] = data[0]['z'] * np.random.rand(*data[0]['z'].shape)

    # let's now create slider for map
    steps = []
    for i in range(len(data)):
        step = dict(method='restyle',
                    args=['visible', [False] * len(data)],
                    label='Year {}'.format(i + 1980))
        step['args'][1][i] = True
        steps.append(step)

    slider = [dict(active=0,
                   pad={"t": 1},
                   steps=steps)]
    layout = dict(geo=dict(scope='usa',
                           projection={'type': 'albers usa'}),
                  sliders=slider)

    fig = dict(data=data,
               layout=layout)

    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

with tab3:
    st.header('Chart with Slider')
    st.write(
        f'In this plot, it is possible to observe the presence of outliers. The ages **around and over 100** are most likely erroneous data inputs. These errors may have been made by accident or on purpose. For instance, some users may not want to disclose their personal information.')

    fig = px.scatter(df_test, x="gdpPercap", y="lifeExp", animation_frame="year", animation_group="country",
                     size="pop", color="continent", hover_name="country",
                     log_x=True, size_max=55, range_x=[100, 100000], range_y=[25, 90])

    fig["layout"].pop("updatemenus")  # optional, drop animation buttons
    fig.update_layout(height=600, width=1000, template=custom_template, xaxis_title='<b>GDP per Capita</b>',
                      yaxis_title='<b>Life Expectation</b>')
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

with tab4:
    st.header('Data')
    st.write(f'In this table, it is possible to observe raw data.')
    columns_to_display = [col for col in df_test.columns if col != 'geometry']
    st.dataframe(df_test[columns_to_display], use_container_width=True)
