from application.plotly_objects import PlotlyMap
from application.algorithm.n_neighbour import NearestNeighbour
from application.algorithm.christ import ChristAlgorithm
from application.algorithm.concord import ConcordAlgorithm
from application.algorithm import PathData

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash
from dash.dependencies import Input, Output, State
import dash_daq as daq
from dash.exceptions import PreventUpdate


import logging
import pandas as pd
import pathlib

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
DEFAULT_ZOOM = 4

""" table loading 
index - cities' names
columns - long, lat
"""

data_xls_path = pathlib.Path(__file__).parent.resolve() / 'assets/gps_cities.xlsx'
df = pd.read_excel(data_xls_path)
df.set_index('city', inplace=True, drop=True)

logger = logging.getLogger('local_writer')
logger.setLevel(logging.DEBUG)

sh = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)


class PathMaker:

    @staticmethod
    def return_path_data(alg: str, work_df: pd.DataFrame):
        if alg == 'NN':
            path_info = NearestNeighbour.path_facility(work_df, work_df.index[0])
        elif alg == 'CA':
            path_info = ChristAlgorithm.path_facility(work_df)
        elif alg == 'CC':
            path_info = ConcordAlgorithm.path_facility(work_df)
        else:
            raise ValueError("Incorrect algorithm type")

        return path_info

    @staticmethod
    def return_path_json(alg: str, work_df: pd.DataFrame) -> dict:

        path_data = PathMaker.return_path_data(alg, work_df)

        return {"distance": path_data.distance,
                "complexity": path_data.complexity,
                "nodes": path_data.nodes_sequence,
                "path_1": path_data.path_sequence,
                "path_2": path_data.second_path_sequence}


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
                    dbc.Label('Distance', style={'margin-left': '5px'})
                ]),
                dbc.Col(children=[
                    dbc.Label(id='complex-label', children=['Complexity'])], style={'margin-left': '5px'})
            ]),
            dbc.Row(children=[
                dbc.Col(children=[
                    daq.LEDDisplay(id='distance-display',
                                   value="0000",
                                   size=22)
                ], width='auto'
                ),
                dbc.Col(children=[
                    daq.LEDDisplay(id='complex-display',
                                   value="0000",
                                   size=22)
                ], width='auto')
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
                          figure=PlotlyMap.cleaned_map(df, zoom=DEFAULT_ZOOM),
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
    [Output('complex-label', 'style'),
     Output('complex-display', 'style')],
    Input('alg-name', 'value')
)
def hide_complexity(alg):
    if alg == 'CC':
        return {'display': 'none'}, {'display': 'none'}
    else:
        return {'display': 'block'}, {'display': 'block'}


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
    Output('path_data', 'data'),
    Input('launch', 'n_clicks'),
    [State('alg-name', 'value'),
     State('local_state', 'data')])
def start_calculations(n, alg, local_state):
    if n:
        if (n > 0) & (local_state is not None):
            if len(local_state['selected']) > 0:
                work_df = df.loc[df.index.isin(local_state['selected'])].copy()
                path = PathMaker.return_path_json(alg, work_df)
                logger.debug(f'Path created: {path}')
                return path
    else:
        raise PreventUpdate


@app.callback(
    [Output('main-graph', 'figure'),
     Output('local_state', 'data'),
     Output('run-timer', 'disabled'),
     Output('distance-display', 'value'),
     Output('complex-display', 'value')
     ],
    [Input('main-graph', 'clickData'),
     Input('main-graph', 'relayoutData'),
     Input('path_data', 'data'),
     Input('run-timer', 'n_intervals'),
     Input('reset', 'n_clicks')
     ],
    [State('run-timer', 'disabled'),
     State('local_state', 'data'),
     State('path_data', 'data')]
)
def display_click_data(
        click_data, rel_data, path_data_trigger, timer,  n_reset,  # inputs
        run_timer_status, local_state, path_data  # states
):
    """
    Main callback updating the graph
    :param click_data: point selection callback
    :param timer: built-in timer callback
    :param rel_data: layout data of the graph
    :param run_timer_status: run-timer state
    :return: Plotly figure for the graph object
    """

    # defines the object which emitted the callback signal
    _ctx = dash.callback_context.triggered[0]['prop_id']
    ctx, ctx_2 = _ctx.split('.')

    if path_data:
        distance = f"{int(path_data['distance']):04.0f}"
        complexity = f"{int(path_data['complexity']):04.0f}"
        nodes = path_data['nodes']
        path_1 = path_data['path_1']
        path_2 = path_data['path_2']

        vis_steps = len(path_1.keys())

    else:
        distance, complexity = '0000', '0000'
        nodes, path_1, path_2 = None, None, None
        vis_steps = -1

    if local_state:
        selected = local_state['selected'] or []
        zoom = local_state['zoom']
        center = local_state['center']
        counter = local_state['counter'] if 'counter' in local_state.keys() else 0
    else:
        selected = []
        zoom = DEFAULT_ZOOM
        center = (df.long.mean(), df.lat.mean())
        counter = -1

    # click on the main graph
    if ctx == 'main-graph':
        if ctx_2 == 'relayoutData':
            if rel_data:
                if 'mapbox.zoom' in rel_data.keys():
                    zoom = rel_data['mapbox.zoom']
                    fig, _, _ = PlotlyMap.get_featured_map(df, selected=selected,
                                                           zoom=zoom, center=center)
                    return fig, {'selected': selected, 'zoom': zoom, 'center': center}, dash.no_update, distance, complexity

                else:
                    return dash.no_update, dash.no_update, dash.no_update, distance, complexity

            else:
                return dash.no_update, dash.no_update, dash.no_update, distance, complexity

        elif ctx_2 == 'clickData':
            if click_data:

                selection = click_data['points'][0]['text']

                if selection in selected:
                    selected.pop(selected.index(selection))
                else:
                    selected.append(selection)

                try:
                    fig, _, _ = PlotlyMap.get_featured_map(df, selected=selected,
                                                           zoom=zoom, center=center)

                    return fig, {'selected': selected, 'zoom': zoom, 'center': center}, dash.no_update, distance, complexity

                except Exception as ex:
                    logger.critical(f'{ex}')
                    raise PreventUpdate

            else:
                return dash.no_update, dash.no_update, dash.no_update, distance, complexity

        else:
            return dash.no_update, dash.no_update, dash.no_update, distance, complexity

    elif ctx == 'path_data':
        logger.debug('Run timer started')
        logger.debug(f'Counter: {counter}')
        logger.debug(f'Visual steps: {vis_steps}')
        fig, _, _ = PlotlyMap.get_featured_map(df, selected=selected, zoom=zoom, center=center,
                                               highlight_path=path_1['0'], second_highlight_path=path_2['0'],
                                               highlight_nodes=nodes['0'])
        return fig, {'selected': selected, 'zoom': zoom, 'center': center, 'counter': counter + 1},\
               False, distance, complexity

    elif ctx == 'run-timer':
        logger.debug('Run timer interval')
        logger.debug(f'Counter: {counter}')
        logger.debug(f'Visual steps: {vis_steps}')
        if counter < vis_steps:
            fig, _, _ = PlotlyMap.get_featured_map(df, selected=selected, zoom=zoom, center=center,
                                                   highlight_path=path_1[str(counter)],
                                                   second_highlight_path=path_2[str(counter)],
                                                   highlight_nodes=nodes[str(counter)])
            return fig, {'selected': selected, 'zoom': zoom, 'center': center, 'counter': counter + 1},\
                   False, distance, complexity
        else:
            return dash.no_update, {'selected': selected, 'zoom': zoom, 'center': center, 'counter': 0}, True, distance, complexity

    elif ctx == 'reset':
        logger.debug('Map reset')
        distance, complexity = '0000', '0000'
        return PlotlyMap.cleaned_map(df, zoom=DEFAULT_ZOOM), \
               {'selected': [], 'zoom': DEFAULT_ZOOM, 'center': center, 'counter': 0}, \
               True, distance, complexity

    else:
        return dash.no_update, dash.no_update, dash.no_update, distance, complexity


# main application layout
app.layout = html.Div([dcc.Location(id='loc', refresh=True),
                       dcc.Interval(id='run-timer', interval=interval_ms, disabled=True),
                       navBar(),
                       html.Div(id='page-content', children=[dashboard()]),
                       dbc.Modal(children=make_modal("NN"), id="modal"),
                       dcc.Store(id='local_state'),
                       dcc.Store(id='path_data')
                       ])
