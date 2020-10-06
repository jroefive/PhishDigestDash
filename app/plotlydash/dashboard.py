"""Create a Dash app within a Flask app."""
import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
from app.functions import reset_sets_list, get_data, get_date, generate_table, get_similar_table_df, generate_figure
from dash.dependencies import Input, Output
import datetime





def create_dashboard(server):
    #Need a background version of dataframe to set options for the date dropdown
    tracks_bg = pd.read_csv('https://jroefive.github.io/track_length_combined')


    #Sets hard assigned for the default show (Big Cypress)
    sets = ['Set 1', 'Set 2']

    #Add Year, Month, and Day columns to the dataframe to make the dropdowns dynamic
    #(You only get options for the months played in the chosen year)
    tracks_bg['year'] = pd.DatetimeIndex(tracks_bg['date']).year
    tracks_bg['month'] = pd.DatetimeIndex(tracks_bg['date']).month
    tracks_bg['day'] = pd.DatetimeIndex(tracks_bg['date']).day

    #Create lists for dropdowns for all shows and all years.
    all_dates = tracks_bg['date'].unique()
    all_years = tracks_bg['year'].unique()

    style_33 = {'width': '33.33%', 'display': 'inline-block'}
    style_25 = {'width': '25%', 'display': 'inline-block'}

    #Initiate the dashboard
    dash_app = dash.Dash(server=server,
                         routes_pathname_prefix='/dashapp/',
                         external_stylesheets=['/static/style.css']
                         )

    #Pull in defaul html saved in layout.py
    #dash_app.index_string = html_layout
    #Create overall layout
    dash_app.layout = html.Div([
            # Input window for dates and graph options.
            html.Div([html.Img(
                src='https://github.com/jroefive/jroefive.github.io/blob/master/photos/phish-donut-stripe.jpg?raw=true',
                style={'width':'100%'}
                               )
            ]
            ),
            html.Div([
                #Date inputs
                html.Div([

                    dcc.Dropdown(id='Show_Date',
                                 options=[{'label': i, 'value': i} for i in all_dates],
                                 placeholder = "Select or Type Date"
                                 ),

                    html.Div([
                    dcc.Dropdown(id='Show_Year',
                                 options=[{'label': i, 'value': i} for i in all_years],
                                 placeholder="Select Year"
                                 )
                    ],
                            style=style_33
                    ),

                    html.Div([
                        dcc.Dropdown(id='Show_Month',
                                     placeholder="Select Month (after year)")
                    ],
                        style=style_33
                    ),

                    html.Div([
                        dcc.Dropdown(id='Show_Day',placeholder="Select Day (after month)")
                    ],
                        style=style_33
                    )
                ],
                    style={'width': '50%', 'margin-top':'25px', 'margin-bottom':'25px', 'display': 'inline-block'}
                ),

                #Graph options inputs
                html.Div([
                    dcc.Dropdown(id='Set',
                                 options=[{'label': i, 'value': i} for i in sets],
                                 value='Set 1'
                                 ),
                    dcc.Dropdown(id='Graph_Type',
                                 options=[{'label': 'Graph Type - Song Duration', 'value': 'Song Duration'},
                                          {'label': 'Graph Type - Set Placement', 'value': 'Set Placement'}
                                          ],
                                 value='Song Duration'
                                 )
                ],
                    style = style_25
                ),

                html.Div([
                    dcc.Dropdown(id='points_to_show',
                                 options=[{'label': 'Show Points for All Times Played', 'value': 'all'},
                                          {'label': 'Show Points only for Outliers', 'value': 'outliers'},
                                          {'label': 'Show only Box Plot', 'value': False}],
                                 value='all'
                                 ),

                    dcc.Dropdown(id='shows_to_highlight',
                                 options=[{'label': 'None', 'value': 'None'},
                                          {'label': 'Highlight Previous 50 Shows', 'value': 'Previous 50 Shows'},
                                          {'label': 'Highlight Selected Show', 'value': 'Selected Show'},
                                          {'label': 'Highlight Next 50 Shows', 'value': 'Next 50 Shows'}],
                                 value='Selected Show'
                                 )
                ],
                    style = style_25
                )
            ],
                style={'width': '90%', 'margin-left':'75px', 'backgroundColor':'#2C6E91'}
            ),

                #Graph placement
                html.Div([dcc.Graph(id='graph_with_input')],
                         style={'width':'90%', 'margin-left':'75px'}
                         ),

                html.P('Click on a point to see details and a link to listen.',
                       style={'color': '#F15A50'}
                       ),

                html.Div([html.P(id='hover-table')],
                         style={'width': '90%', 'color': '#F15A50', 'text-align': 'center',
                                'backgroundColor': '#2C6E91',
                                'margin-left':'75px', 'verticalAlign': 'center', 'min-height': '10px'}
                         ),

                html.P('Shows that are the most similar to the selected show.',
                       style={'color': '#F15A50'}
                       ),

                html.Div([html.P(id='similar-table')],
                         style={'width': '90%', 'color': '#F15A50', 'text-align': 'center',
                                'backgroundColor': '#2C6E91', 'min-height': '10px', 'margin-left':'75px',
                                'verticalAlign': 'center'
                                }
                         ),

                html.P('Feedback and feature requests welcome: jroefive@gmail.com',
                       style={'color': '#F15A50', 'text-align': 'center', 'height': '50px'}
                       ),

            dcc.Link('o          Phish Song Graphs          ',
                     href='https://the-story-of-a-phish-song.wl.r.appspot.com/dashapp/',
                     style={'color': '#F15A50'}
                     ),

            dcc.Link('o          Phish Tour Analysis          ',
                     href='https://phish-tour-analysis.wl.r.appspot.com/dashapp/',
                     style={'color': '#F15A50'}
                     ),

            dcc.Link('o          Phish Set Closer Prediction          o',
                     href='https://predicting-phish-set-closers.wl.r.appspot.com/dashapp/',
                     style={'color': '#F15A50'}
                     ),

            html.Div([html.Img(
                src='https://github.com/jroefive/jroefive.github.io/blob/master/photos/phish-donut-stripe.jpg?raw=true',
                style={'width':'100%'}
            )
            ]
            )
    ],
        style={'text-align': 'center','backgroundColor':'#2C6E91'}
    )


    #Update the month options after a year is chosen
    @dash_app.callback(
        Output('Show_Month', 'options'),
        [Input('Show_Year', 'value')
         ]
    )
    def set_month_options(show_year):
        month_options_pd = tracks_bg[tracks_bg['year']==show_year].copy()
        month_options = month_options_pd['month'].unique()
        return [{'label': i, 'value': i} for i in month_options]

    #Update the day options once a month is chosen.
    @dash_app.callback(
        Output('Show_Day', 'options'),
        [Input('Show_Year', 'value'),
         Input('Show_Month', 'value'),
         ]
    )
    def set_day_options(show_year, show_month):
        day_options_pd = tracks_bg[(tracks_bg['year']==show_year) & (tracks_bg['month']==show_month)].copy()
        day_options = day_options_pd['day'].unique()
        return [{'label': i, 'value': i} for i in day_options]

    #Reset show_date once a day is chosen
    @dash_app.callback(
        Output('Show_Date', 'value'),
        [Input('Show_Day', 'value'),
        Input('Show_Year', 'value'),
        Input('Show_Month', 'value')
         ]
    )
    def set_date(day, year, month):
        show_date = datetime.date(year, month, day)
        return show_date

    #Reset list of sets every time a show_date is changed
    @dash_app.callback(
        Output('Set', 'options'),
        [Input('Show_Date', 'value')
         ]
    )
    def set_month_options(show_date):
        sets = reset_sets_list(show_date)
        return [{'label': i, 'value': i} for i in sets]

    #Redraw figure every time any of the inputs change
    @dash_app.callback(
        Output('graph_with_input', 'figure'),
        [Input('Set', 'value'),
         Input('Graph_Type', 'value'),
         Input('Show_Date', 'value'),
         Input('points_to_show', 'value'),
         Input('shows_to_highlight', 'value')
         ]
    )
    def draw_fig(set, graph_type, show_date, points_to_show, shows_to_highlight):
        #Call the get_date function to get the setlist and two graph input dictionaries
        graph_data_dict, set_songs, graph_highlight_dict = get_data(set, graph_type, show_date, shows_to_highlight)

        #Initiate the figrue
        figure = generate_figure(set_songs, graph_data_dict, points_to_show, shows_to_highlight,
                                 graph_highlight_dict, graph_type
                                 )

        return figure

    #Update table every time a point is clicked or change to help test when the graph is changed
    @dash_app.callback(
        Output('hover-table', 'children'),
        [Input('graph_with_input', 'clickData'),
        Input('Show_Date', 'value'),
        Input('Graph_Type', 'value')
         ]
    )
    def update_song_table(clickData, date, graph_type):
            date_link_df = get_date(clickData, date, graph_type)
            return generate_table(date_link_df)

    #Update table every time a point is clicked or change to help test when the graph is changed
    @dash_app.callback(
        Output('similar-table', 'children'),
        [Input('Show_Date', 'value')
         ]
    )
    def update_similar_table(date):

        df = get_similar_table_df(date)
        return generate_table(df)



    return dash_app.server
