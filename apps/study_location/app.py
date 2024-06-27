import os
import pandas as pd
import geopandas as gpd
from dash import dcc, Dash
from dash import html
from dash import dash_table
import plotly.express as px
from dash.dependencies import Input, Output


# Load and prepare data
def get_data():
    print("Loading data")
    country_mapping = pd.read_json('data/country_mapping.json', orient='records', encoding='utf-8')
    country_shapes = gpd.read_file(
        'https://services.arcgis.com/B7NI2jUD81lCgSpx/arcgis/rest/services/Assignment_6_Spatial_Reference_Systems/FeatureServer/1/query?outFields=*&where=1%3D1&f=geojson')
    df = pd.read_csv('data/study_location_data.csv')

    country_shapes = country_shapes.merge(country_mapping, left_on='CNTRY_NAME', right_on='geoName', how='left')
    geo_df = df.merge(country_mapping, left_on='country', right_on='geoName')
    geo_df = country_shapes.merge(geo_df, left_on='code', right_on='code', how='left')
    geo_df = geo_df[geo_df['CNTRY_NAME'] != 'Antarctica']

    # Load world population data
    population_data = pd.read_csv('data/world_population.csv')
    population_data.rename(columns={'2022 Population': 'population'}, inplace=True)

    # Merge population data based on the CCA3 code
    geo_df = geo_df.merge(population_data[['CCA3', 'population']], left_on='CCA3_x', right_on='CCA3', how='left')

    # Add extra column number / population
    geo_df['papers_per_capita'] = geo_df['number'] / geo_df['population'] * 1e+6

    # Final renaming and cleaning
    geo_df.rename(columns={'country': 'country_data', 'CNTRY_NAME': 'country'}, inplace=True)

    # remove unused columns
    geo_df.drop(columns=['CCA3_x', 'CCA3_y', 'CCA3', 'country_data'], inplace=True)
    geo_df['number'] = geo_df['number'].fillna(0)
    return geo_df


# Data example for the paper list
papers_examples = [
    {
        'title': 'Deep Learning for AI',
        'url': 'https://example.com/deep_learning',
        'authors': 'Jane Doe, John Smith',
        'publication_place': 'Journal of AI Research, 2021'
    },
    {
        'title': 'Advances in Computer Vision',
        'url': 'https://example.com/computer_vision',
        'authors': 'Jane Doe, Emily Stone',
        'publication_place': 'Conference on Computer Vision, 2022'
    }
]


def generate_markup(papers):
    markup = ""
    for paper in papers:
        title = paper.get('title', 'No Title Available')
        url = paper.get('url', '#')
        authors = paper.get('authors', 'Anonymous')
        publication_place = paper.get('publication_place', 'Unknown Venue')

        # Construct the markup for each paper using Markdown format
        paper_markup = f'[{title}]({url})  \n'  # Markdown link and two spaces for a line break
        paper_markup += f'{authors}  \n'  # Two spaces at the end for a Markdown line break
        paper_markup += f'{publication_place}\n\n'  # Extra newline to separate entries

        # Append the current paper's markup to the overall markup string
        markup += paper_markup

    return markup


geo_df = get_data()
# keep only rows with number > 0
geo_filtered_df = geo_df[geo_df['number'] > 0]

# Assuming your color_continuous_scale is defined as follows:
color_continuous_scale = [
    (0.0, '#fefefe'),  # no data
    (0.01, '#fde725'),  # rgb(253, 231, 37) or #fde725
    (0.17, '#90d743'),  # rgb(144, 215, 67) or #90d743
    (0.33, '#35b779'),  # rgb(53, 183, 121) or #35b779
    (0.50, '#21918c'),  # rgb(33, 145, 140) or #21918c
    (0.67, '#31688e'),  # rgb(49, 104, 142) or #31688e
    (0.83, '#443983'),  # rgb(68, 57, 131) or #443983
    (1.0, '#440154')  # rgb(68, 1, 84) or #440154
]


def adjust_color_scale(geo_df, color_scale):
    max_value = geo_df['number'].max()
    return [[int(frac * max_value), color] for frac, color in color_scale]


adjusted_color_scale = adjust_color_scale(geo_df, color_continuous_scale)

# Initialize Dash app
base_url_path = os.environ.get('BASE_URL_PATH', '')
app = Dash(__name__,
           suppress_callback_exceptions=True,
           url_base_pathname=f"/{base_url_path}/" if base_url_path else "/"
           )

app._favicon = ("favicon.png")
app.title = "Digital Divide, Study Location"
server = app.server

columns_to_display = [col for col in geo_df.columns if
                      col not in ['geometry', 'geoName_y', 'geoName_x', 'OBJECTID']]
# Layout of the app
app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='Map', value='tab-1', children=[
            html.Div([
                html.H4('Global Study Distribution Map'),
                dcc.Graph(
                    figure=px.choropleth(geo_df,
                                         locations='country',
                                         locationmode='country names',
                                         color="number",
                                         hover_name="country",
                                         labels={'number': 'Number of studies'},
                                         color_continuous_scale=color_continuous_scale,
                                         range_color=[0, geo_df['number'].max()])
                    .update_geos(fitbounds='locations', visible=False)
                    .update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0}),
                    id="map",
                )
            ]),
        ]),
        dcc.Tab(label='Data', value='tab-2', children=[
            html.Div([
                html.H4('Detailed Data Table'),
                dash_table.DataTable(
                    data=geo_filtered_df[columns_to_display].to_dict('records'),
                    columns=[{'name': i, 'id': i} for i in columns_to_display],
                    style_table={'overflowX': 'auto'},
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    page_action="native",
                    page_current=0,
                    page_size=10,
                    id='data-table'
                )
            ])
        ]),
        dcc.Tab(label='Graph', value='tab-3', children=[
            html.Div(children=[
                html.H4('Publications by Country'),
                dcc.Dropdown(geo_filtered_df.country.unique(), value='United Kingdom', id='country-selection'),
                html.Div(id='papers-div')
            ]),
        ]),
    ]),
    html.Div(id='tabs-content')
])


@app.callback(
    # Output("graph", "figure"),
    Output("country-selection", "value"),
    [Input("map", "clickData")]
)
def mapClick(clickData):
    return clickData['points'][0]['location'] if clickData else ""


@app.callback(
    Output('papers-div', 'children'),
    [Input('country-selection', 'value')]
)
def update_data(value):
    papers_count = ""
    try:
        # print("value selected: ", value)
        dff = geo_df[geo_df.country == value]
        # print("dff: ", dff)
        papers = dff['papers'].values[0]
        papers_count = f" {int(dff['number'].values[0])} papers"
        print("papers data: ", papers)
    except:
        papers = "No data available for this country."

    markup_text = generate_markup(papers_examples)
    div = [
        dcc.Markdown(f'''

### paper data: {papers} {papers_count}


----------
{markup_text}
----------
        '''),
        # px.bar(pd.DataFrame({"x": [], "y": []}))
    ]
    return div
    # dff = df[df.country==value]
    # return px.line(dff, x='year', y='pop')


@app.callback(Output("tabs", "value"),
              Input("map", "clickData"))
def select_tab(clickData):
    if clickData:
        # Change tab to the third one after clicking on the map
        return "tab-3"
    return "tab-1"


if __name__ == '__main__':
    app.run_server(debug=False,
                   dev_tools_hot_reload=False)
