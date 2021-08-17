import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash
from dash.dependencies import Input, Output, State
import pandas as pd
import dash_daq as daq
from dash.exceptions import PreventUpdate
from algorithm.algorithm import NearestNeighbour
from algorithm.christ import ChristAlgorithm
from algorithm.concord import ConcordAlgorithm
from plotly_objects import BaseMap

alg_lst = [{'label': 'Nearest Neighbor', 'value': 'NN'},
           {'label': 'Christofides Algorithm', 'value': 'CA'},
           {'label': 'Concorde Algorithm', 'value': 'CC'}]

header = {"NN": 'Nearest neighbour algorithm',
          "CA": 'Christofides algorithm',
          "CC": 'Concorde Algorithm'}

body = {
    "NN": 'The nearest neighbour algorithm was one of the first algorithms used to solve the travelling salesman problem'
          ' approximately. In that problem, the salesman starts at a random city and repeatedly visits the '
          'nearest city until all have been visited. The algorithm quickly yields a short tour, but usually not '
          'the optimal one.',
    "CA": 'The Christofides algorithm or Christofides–Serdyukov algorithm is an algorithm for finding approximate '
          'solutions to the travelling salesman problem, on instances where the distances form a metric space ('
          'they are symmetric and obey the triangle inequality). It is an approximation algorithm that '
          'guarantees that its solutions will be within a factor of 3/2 of the optimal solution length, '
          'and is named after Nicos Christofides and Anatoliy I. Serdyukov, who discovered it independently in '
          '1976.',
    "CC": 'Concorde algorithm (suboptimal)'}

interval_ms = 2000

""" table loading 
index - cities' names
columns - long, lat
"""

df = pd.read_excel('assets/gps_cities.xlsx')
df['checked'] = False
df.set_index('city', inplace=True, drop=True)

path, path_2, nodes, time_tracking = {}, {}, {}, {}
counter, distance, complexity = 0, 0, 0
highlight_path, second_highlight_path, highlight_nodes = [], [], []

pause_state = False

main_figure = BaseMap(cities=df)


def navBar():
    """
    Simple NavBar constructor
    :return:
    """
    navbar = dbc.NavbarSimple(
        children=[],
        brand="Tradesman problem v.2",
        brand_href="/",
        color="primary",
        dark=True,
    )
    return navbar


def dashboard():
    """
    DashBoard HTML constructor
    :return:
    """

    # controls (left upper panel)
    controls = dbc.Card(
        [
            dbc.FormGroup(
                [
                    dbc.Label('Algorithm choice'),
                    dbc.Row(children=[
                        dbc.Col(
                            dcc.Dropdown(id='alg-name',
                                         options=alg_lst,
                                         value='NN',
                                         multi=False,
                                         style={'vertical-align': 'center',
                                                'margin-right': '-1px',
                                                'margin-left': '-1px'})
                        )
                    ]
                    )
                ]),
            dbc.Row(children=[
                dbc.Button('Run', id='launch', color='success', className='mr-1',
                           style={'width': '112px'}),
                dbc.Button('Reset', id='reset', color='danger', className='mr-1',
                           style={'width': '112px', 'margin-left': '10px'})

            ], justify='center'
            ),
            dbc.Row(children=[
                dbc.Button('Pause', id='pause', color='primary', className='mr-1',
                           style={'width': '112px'}, disabled=True),
                dbc.Button('Info', id='help', color='secondary', className='mr-1',
                           style={'width': '112px', 'margin-left': '10px'})

            ], justify='center', style={'margin-top': '8px'}
            )
        ], style={'margin': '20px'}, body=True
    )

    # gauges (left lower panel)
    gaudges = dbc.Card(
        [
            dbc.Row(children=[
                dbc.Col(children=[
                    dbc.Label('Complexity')], style={'margin-left': '5px'}),
                dbc.Col(children=[
                    dbc.Label('Distance')
                ])
            ]),
            dbc.Row(children=[
                dbc.Col(children=[
                    daq.LEDDisplay(id='complex-display',
                                   value="0000",
                                   size=22)
                ], width='auto'),
                dbc.Col(children=[
                    daq.LEDDisplay(id='distance-display',
                                   value="0000",
                                   size=22)
                ], width='auto'
                )
            ]
            )
        ], body=True, style={'margin-right': '20px', 'margin-left': '20px'}
    )

    # main layout
    layout = dbc.Container([
        dbc.Row(children=[
            dbc.Col(children=[
                dbc.Row(children=[controls]),
                dbc.Row(children=[gaudges])
            ],
                md=3, width='auto'),
            dbc.Col(children=[
                # main graph constructor
                dcc.Graph(id='main-graph',
                          figure=main_figure.get_map(initial=True),
                          style={'margin-top': '20px'},
                          config={'scrollZoom': True}),

            ],
                md=9, width='auto')]
        ),
        html.Div(id='dummy'),
    ],
        fluid=True)

    return layout


def make_modal(alg_name):
    return [dbc.ModalHeader(header[alg_name]),
            dbc.ModalBody(html.Div(children=body[alg_name], style={'text-justify': 'center', 'align': 'center'})),
            dbc.ModalFooter(
                dbc.Button("Close", id="close", className="ml-auto")
            )]


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True
server = app.server


@app.callback(
    [Output("collapse-body", "is_open"),
     Output("info-header", "children"),
     Output("info-body", "children")],
    [Input("help", "n_clicks")],
    [State("collapse-body", "is_open"),
     State("alg-name", "value")],
)
def toggle_collapse(n, is_open, alg_name):
    global header, body
    """
    Callback for collapsing window
    :param n: callback of the ? button
    :param is_open: state of the window to change it
    :param alg_name: state of the ComboBox which defines current chosen algorithm
    :return: change collapse body flag, header and body of the info collapsing window
    """
    if n:
        if not is_open:
            header = alg_name
            body = f'About {alg_name}'
        return not is_open, header, body
    return is_open, "", ""


@app.callback(
    [Output("modal", "is_open"), Output("modal", "children")],
    [Input("help", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open"), State("alg-name", "value")],
)
def toggle_modal(n1, n2, is_open, alg_name):
    """
    Opens model window with the proper text
    :param n1: Help button clicked
    :param n2: Close button in the model window clicked
    :param is_open: boolean Model window opened flag
    :param alg_name: Current chosen algorithm name
    :return: Change modal window flag and return children for its instance inherited in the page
    """
    if n1 or n2:
        return not is_open, make_modal(alg_name)
    return is_open, make_modal(alg_name)


@app.callback(
    [Output('main-graph', 'figure'),
     Output('run-timer', 'disabled'),
     Output('distance-display', 'value'),
     Output('complex-display', 'value'),
     Output('pause', 'disabled'),
     Output('pause', 'children')],
    [Input('main-graph', 'clickData'),
     Input('launch', 'n_clicks'),
     Input('run-timer', 'n_intervals'),
     Input('alg-name', 'value'),
     Input('reset', 'n_clicks'),
     Input('main-graph', 'relayoutData'),
     Input('pause', 'n_clicks')],
    State('run-timer', 'disabled')
)
def display_click_data(click_data, n, timer, alg, n2, rel_data, n3, run_timer_status):
    """
    Main callback updating the graph
    :param click_data: point selection callback
    :param n: launch button callback
    :param timer: built-in timer callback
    :param alg: combobox callback (current value)
    :param n2: reset button callback
    :param n3: pause button callback
    :param rel_data: layout data of the graph
    :param run_timer_status: run-timer state
    :return: Plotly figure for the graph object
    """
    global path, path_2, nodes, time_tracking, counter, highlight_nodes, highlight_path, second_highlight_path, \
        distance, complexity, interval_ms, pause_state

    # defines the object which emitted the callback signal
    _ctx = dash.callback_context.triggered[0]['prop_id']
    ctx, ctx_2 = _ctx.split('.')
    main_figure.selected = df.loc[df.checked == True]

    # click on the main graph
    if ctx == 'main-graph':
        if ctx_2 == 'relayoutData':
            if 'mapbox.zoom' in rel_data.keys():
                main_figure.zoom = rel_data['mapbox.zoom']
        else:
            if click_data:
                df.loc[click_data['points'][0]['text'], 'checked'] = not (
                df.loc[click_data['points'][0]['text'], 'checked'])
                main_figure.selected = df.loc[df.checked == True]
                return main_figure.get_map(),\
                       True,\
                       "0000",\
                       "0000",\
                       True,\
                       'Pause'
            else:
                raise PreventUpdate

    # click on the Reset button
    if ctx == 'reset':
        main_figure.cleaned_map(selected=True)
        if n2 > 0:
            df.checked = False
            return main_figure.get_map(initial=True),\
                   True,\
                   "0000",\
                   "0000",\
                   True,\
                   'Pause'
        else:
            raise PreventUpdate

    # click on the Launch button
    elif ctx == 'launch':
        if n > 0:
            work_df = df.loc[df.checked == True].copy()
            work_df.drop(columns=['checked'], inplace=True)
            main_figure.cleaned_map()

            if len(work_df) > 0:
                if alg == 'NN':
                    nn = NearestNeighbour(work_df, work_df.index[0])
                elif alg == 'CA':
                    nn = ChristAlgorithm(work_df)
                elif alg == 'CC':
                    nn = ConcordAlgorithm(work_df)
                else:
                    raise ValueError("Incorrect algorithm type")

                path = nn.path_sequence

                try:
                    path_2 = nn.second_path_sequence
                except:
                    path_2 = {k: [] for k, v in path.items()}
                nodes = nn.nodes_sequence
                distance = nn.distance
                complexity = nn.complexity
                return main_figure.get_map(),\
                       False,\
                       "0000",\
                       "0000",\
                       False,\
                       'Continue' if pause_state else 'Pause'

            return main_figure.get_map(),\
                   True,\
                   "0000",\
                   "0000",\
                   False,\
                   'Pause'
        else:
            raise PreventUpdate

    elif ctx == 'pause':
        if counter != 0:
            pause_state = not pause_state
            return main_figure.get_map(highlight_path=highlight_path,
                                       second_highlight_path=second_highlight_path,
                                       highlight_nodes=highlight_nodes), \
                not run_timer_status,\
                   "0000",\
                   "0000",\
                   False, \
                   'Continue' if pause_state else 'Pause'
        else:
            return main_figure.get_map(),\
                   not run_timer_status,\
                   "0000",\
                   "0000",\
                   True, \
                   'Pause'

    # run-timer event (set for 1s interval)
    elif ctx == 'run-timer':
        if counter < len(path):
            highlight_path = path[counter]
            second_highlight_path = path_2[counter]
            highlight_nodes = nodes[counter]
            counter += 1
            return main_figure.get_map(highlight_path=highlight_path,
                                       second_highlight_path=second_highlight_path,
                                       highlight_nodes=highlight_nodes), \
                   False,\
                   "0000",\
                   "0000",\
                   False, \
                   'Continue' if pause_state else 'Pause'
        else:
            counter = 0
            return main_figure.get_map(highlight_path=highlight_path,
                                       second_highlight_path=second_highlight_path,
                                       highlight_nodes=highlight_nodes), \
                   True,\
                   f'{distance:04.0f}',\
                   f'{float(complexity):04.0f}' if isinstance(complexity, int) else complexity,\
                   True,\
                   'Pause'

    # the figure shouldn't be updated
    else:
        raise PreventUpdate


# main application layout
app.layout = html.Div([dcc.Location(id='loc', refresh=True),
                       dcc.Interval(id='run-timer', interval=interval_ms, disabled=True),
                       navBar(),
                       html.Div(id='page-content', children=[dashboard()]),
                       dbc.Modal(children=make_modal("NN"), id="modal")
                       ])

if __name__ == '__main__':
    app.run_server(debug=False)
