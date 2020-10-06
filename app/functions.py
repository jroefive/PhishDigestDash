import pandas as pd
import dash_table
import numpy as np
import plotly.graph_objects as go

#Retrieve the ID number of the show that user inputs.
def get_show_date_id(date):
    track_length_combined = pd.read_csv('https://jroefive.github.io/track_length_combined')
    show_date = str(date)

    # Make sure the date input is in the database
    show_date_id = track_length_combined[track_length_combined['date']==show_date]['order_id'].values

    # Previous line creates a series of the same ID values, so need to reset to equal just the first value.
    show_date_id = show_date_id[0]
    return show_date_id

# Check to see how many songs are in each set of the show and if a set has a song then include that as an option to view
def reset_sets_list(show_date):
    sets = []
    show_id  = get_show_date_id(show_date)
    track_length_combined = pd.read_csv('https://jroefive.github.io/track_length_combined')
    show_only = track_length_combined[(track_length_combined['order_id']==show_id)]
    show_only = show_only.sort_values(by='position')
    show_songs_s1 = show_only[show_only['set']=='1']['title'].values
    if len(show_songs_s1)>0:
        sets.append('Set 1')

    show_songs_s2 = show_only[show_only['set']=='2']['title'].values

    if len(show_songs_s2)>0:
        sets.append('Set 2')

    show_songs_s3 = show_only[show_only['set']=='3']['title'].values

    if len(show_songs_s3)>0:
        sets.append('Set 3')

    show_songs_e = show_only[(show_only['set']=='E') | (show_only['set']=='E2')]['title'].values

    if len(show_songs_e)>0:
        sets.append('Encore')
        
    return sets

#Export data from dataframe as songlist for set and dicts for graphing go.Box
def get_data(set, type, date, shows_to_highlight):
    #Pull in every track in every show and the duration of the song,
    #need a second version of this because the set placement df doesn't have a set column
    tracks_df = pd.read_csv('https://jroefive.github.io/track_length_combined')
    #Set the graphing df based on graph type input
    if type == 'Song Duration':
        tracks_graph = pd.read_csv('https://jroefive.github.io/track_length_combined')
    elif type == 'Set Placement':
        tracks_graph = pd.read_csv('https://jroefive.github.io/set_placement_plot')

    #Get show_id and all the songs played in the show then sort by position in show for graph display
    show_id = get_show_date_id(date)
    show_songs = tracks_df[tracks_df['order_id'] == show_id]
    show_songs = show_songs.sort_values(by=['position'])

    #Slice off just the songs that were played in the chosen set
    if set == 'Set 1':
        set_songs = show_songs[show_songs['set'] == '1']['title'].values
    elif set == 'Set 2':
        set_songs = show_songs[show_songs['set'] == '2']['title'].values
    elif set == 'Set 3':
        set_songs = show_songs[show_songs['set'] == '3']['title'].values
    elif set == 'Encore':
        set_songs = show_songs[(show_songs['set'] == 'E') | (show_songs['set'] == 'E2')]['title'].values

    #Final dataframe which includes all tracks that match the titles of songs chosen date and set
    tracks_from_set = tracks_graph[tracks_graph['title'].isin(set_songs)].copy()

    #Set up empty dictionaries for input into graphs
    graph_data_dict = {}
    graph_highlight_dict = {}

    #Iterate through all songs in the set and add that song to the graph dictionary as
    #the key and a list of all the durations of all times played as the value
    #Repeat for the highlighted shows by returning the same dict but only for the shows in the given range
    for song in set_songs:
        if type == 'Song Duration':
            graph_data_dict[song] = tracks_from_set[tracks_from_set['title'] == song]['duration'].values
            if shows_to_highlight == 'Selected Show':
                graph_highlight_dict[song] = tracks_from_set[
                    (tracks_from_set['title'] == song) & (tracks_from_set['order_id'] == show_id)]['duration'].values

            elif shows_to_highlight == 'Previous 50 Shows':
                graph_highlight_dict[song] = tracks_from_set[
                    (tracks_from_set['title'] == song) & (tracks_from_set['order_id'] < show_id)
                    & (tracks_from_set['order_id'] >= (show_id-50))]['duration'].values

            elif shows_to_highlight == 'Next 50 Shows':
                graph_highlight_dict[song] = tracks_from_set[
                    (tracks_from_set['title'] == song) & (tracks_from_set['order_id'] > show_id)
                    & (tracks_from_set['order_id'] <= (show_id+50))]['duration'].values

        elif type == 'Set Placement':
            graph_data_dict[song] = tracks_from_set[tracks_from_set['title'] == song]['percentintoset'].values
            if shows_to_highlight == 'Selected Show':
                graph_highlight_dict[song] = tracks_from_set[
                    (tracks_from_set['title'] == song)
                    & (tracks_from_set['order_id'] == show_id)]['percentintoset'].values

            elif shows_to_highlight == 'Previous 50 Shows':
                graph_highlight_dict[song] = tracks_from_set[
                    (tracks_from_set['title'] == song) & (tracks_from_set['order_id'] < show_id)
                    & (tracks_from_set['order_id'] >= (show_id - 50))]['percentintoset'].values

            elif shows_to_highlight == 'Next 50 Shows':
                graph_highlight_dict[song] = tracks_from_set[
                    (tracks_from_set['title'] == song) & (tracks_from_set['order_id'] > show_id)
                    & (tracks_from_set['order_id'] <= (show_id + 50))]['percentintoset'].values

    return graph_data_dict, set_songs, graph_highlight_dict


# Pulls out all shows that match the points that were clicked on
def get_date(clickData, date, graph_type):
    val = clickData['points'][0]['y']
    song = clickData['points'][0]['x']

    # Pull only rows from the df that fit criteria
    if graph_type == 'Song Duration':
        all_tracks = pd.read_csv('https://jroefive.github.io/track_length_combined')
        df = all_tracks[(all_tracks['title'] == song) & (all_tracks['duration'] == val)]
        order_ids = list(df['order_id'].values)
        df['Part of Segue?'] = ''
        song_count = 1
        for i in order_ids:
            other_show_tracks = all_tracks[all_tracks['order_id'] == i]
            song_count_df = other_show_tracks[other_show_tracks['title'] == song]
            if song_count_df.shape[0] > 1:
                song_count = 2
                df.loc[df['order_id'] == i, 'Part of Segue?'] = 'Yes'

        display_cols = ['title', 'date', 'set', 'position', 'duration', 'order_id', 'Part of Segue?']
        df1 = df[display_cols]

        df1['min'] = df1['duration'].astype(int)
        df1['minutes'] = df1['min'].astype(str)
        df1['part'] = df1['duration'] % 1
        df1['sec'] = df1['part'] * 60
        df1['secs'] = df1['sec'].astype(int)
        df1['seconds'] = df1['secs'].astype(str)

        for i in range(0, 10):
            df1 = df1.replace({'seconds': str(i)}, '0' + str(i))

        df1['Song Duration'] = df1['minutes'] + ':' + df1['seconds']

    elif graph_type == 'Set Placement':
        all_tracks = pd.read_csv('https://jroefive.github.io/set_placement_plot')
        df = all_tracks[(all_tracks['title'] == song) & (all_tracks['percentintoset'] == val)]
        df['Part of Segue?'] = ''
        order_ids = list(df['order_id'].values)
        song_count = 1
        for i in order_ids:
            other_show_tracks = all_tracks[all_tracks['order_id'] == i]
            song_count_df = other_show_tracks[other_show_tracks['title'] == song]
            if song_count_df.shape[0] > 1:
                song_count = 2
                df.loc[df['order_id'] == i, 'Part of Segue?'] = 'Yes'

        display_cols = ['', 'date', 'percentintoset', 'order_id', 'Part of Segue?']
        df1 = df[display_cols]

        # Adjust the percentintoset column to better explain what it means in the table
        df1['set'] = df['percentintoset'].astype(int)
        df1['percent'] = df['percentintoset'] % 1 * 100
        df1['percent'] = df1['percent'].astype(int)
        df1['percent'] = df1['percent'].astype(str)
        df1 = df1.replace({'set': 4}, 'enc')
        df1['Set Placement'] = df1['percent'] + '% into '
        df1 = df1.replace({'Set Placement': '0% into '}, 'Start of')

    # Create a link column in markdown language so that it shows up as a link
    slugs_df = pd.read_csv('data/slugs')
    slug = slugs_df[slugs_df['title'] == song]['slug'].values
    df1['slug'] = slug[0]
    df1['Link'] = '[Link](https://phish.in/' + df1['date'] + '/' + df1['slug'] + ')'

    # Pull out only the columns for display
    if graph_type == 'Song Duration':
        if song_count > 1:
            final_display_cols = ['title', 'date', 'set', 'position', 'Song Duration', 'Part of Segue?', 'Link']
        else:
            final_display_cols = ['title', 'date', 'set', 'position', 'Song Duration', 'Link']
    elif graph_type == 'Set Placement':
        if song_count > 1:
            final_display_cols = ['title', 'date', 'Set Placement', 'set', 'Part of Segue?', 'Link']
        else:
            final_display_cols = ['title', 'date', 'Set Placement', 'set', 'Link']

    df1 = df1[final_display_cols]
    return df1

#Generate click table
def generate_table(df):
    return dash_table.DataTable(
        data=df.to_dict('records'),
        style_header={'textAlign':'left', 'color':'#2C6E91','fontWeight': 'bold', 'fontSize':'20'},
        style_data={'whiteSpace': 'normal','margin-left':'10px'},
        columns=[{'id': c, 'name': c, 'presentation': 'markdown'} for c in df.columns],
        style_cell={'width': '75px', 'backgroundColor': '#e5ecf6'},
        style_data_conditional=[
            {
                'if': {
                    'column_id': 'Link',
                },
                'fontWeight': 'bold',
            },
            {
                'if': {
                    'column_id': 'Listen',
                },
                'fontWeight': 'bold',
                'marginLeft':'10px'
            },
            {
                'if': {
                    'column_id': 'Shared Songs',
                },

                'width': '400px'
            },
        ])

def flatten_list(list):
    final_list = []
    for date, val in list.items():
        lists = [date, val[0][0], str(round(val[0][1]*100)) + '%', str(round(val[0][2]*100)) + '%',
                 str(round(val[0][3]*100)) + '%', '', ''.join(val[1])
                 ]
        final_list.append(lists)
    return final_list


def get_similar_table_df(date):
    date_top5_dict = np.load('data/all_dates_top5_dict_all_shows.npy', allow_pickle=True).item()
    song_list = date_top5_dict[date]

    song_list_flat = flatten_list(song_list)
    columns = ['Date', '# of Shared Songs', '% of Selected Show',
               '% of Matched Show', '% of Both Shows', 'Shared Songs'
               ]

    df = pd.DataFrame(song_list_flat, columns=columns)
    df['Listen'] = '[Listen](https://phish.in/' + df['Date'] + ')'
    return df

def generate_figure(set_songs, graph_data_dict, points_to_show, shows_to_highlight, graph_highlight_dict, graph_type):
    figure = go.Figure()
    # Iterate through all songs in the set and create a boxplot trace for that song
    for song in set_songs:
        figure.add_trace(go.Box(y=graph_data_dict[song], name=song,
            # Inclue all points, or outliers, or just the box plot based on dropdown input
            boxpoints=points_to_show,
            # Overlay points and box to keep graph compact
            pointpos=0,
            # Include the mean and standard deviation in box plot
            boxmean='sd',
            # Set points to spread out a bit
            jitter=.8,
            # Set markers to be donuts and have the same blue color as the official Phish donut logo
            marker=dict(color='#2C6E91', symbol='circle-open', opacity=0.5, line_width=2),
            marker_size=4
                                )
                         )

        # As long as the highlighted shows isn't None, draw a second trace that only includes the chosen shows
        if shows_to_highlight != 'None':
            figure.add_trace(go.Box(y=graph_highlight_dict[song], name=song, boxpoints=points_to_show,
                                    pointpos=0, jitter=.6,
                                    marker=dict(color='#F15A50', symbol='circle-open', opacity=0.5, line_width=2),
                                    line_width=0.5, marker_size=7.5
                                    )
                             )

    # Basic layout for graph
    figure.update_layout(yaxis=dict(autorange=True, automargin=True, showgrid=True, zeroline=True, dtick=5,
                                    gridcolor='rgb(255, 255, 255)', gridwidth=1, zerolinecolor='#2C6E91',
                                    zerolinewidth=2
                                    ),
                         margin=dict(l=100, r=40, t=40, b=40),
                         paper_bgcolor='#2C6E91',
                         font=dict(family='Arial, monospace', size=18, color='#F15A50'),
                         showlegend=False
                         )

    # For the set placement graphs, eset the numerical values of the y tick labels to match what they mean in context
    if graph_type == 'Set Placement':
        figure.update_layout(yaxis=dict(tickmode='array',
                                        tickvals=[1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5],
                                        ticktext=['Start Set 1', 'Mid Set 1', 'Start Set 2', 'Mid Set 2',
                                                  'Start Set 3', 'Mid Set 3', 'Start Encore', 'Mid Encore',
                                                  'End of Show'
                                                  ]
                                        )
                             )

    # If it is the song duration graph, set the y axis label correctly
    else:
        figure.update_layout(yaxis_title='Song Duration in Minutes', )

    return figure